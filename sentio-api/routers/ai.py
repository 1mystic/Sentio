import asyncio
import json
import logging
import time

from fastapi import APIRouter, Header, HTTPException, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from routers._auth_helpers import get_user_id
from services.badge_engine import check_and_award_badges
from services.claude_service import stream_response
from services.rag_service import rag_query
from services.safety import safety
from services.supabase_client import get_supabase
import services.memory_service as memory_service

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory TTL cache for per-user personalisation context (bias profile + journal themes).
# Avoids 2 extra DB round-trips on every chat message. TTL = 5 minutes.
_USER_CTX_CACHE: dict[str, tuple[float, dict, list]] = {}
_USER_CTX_TTL = 300  # seconds


def _get_user_context(user_id: str, supabase) -> tuple[dict, list[str]]:
    cached = _USER_CTX_CACHE.get(user_id)
    if cached and time.monotonic() - cached[0] < _USER_CTX_TTL:
        return cached[1], cached[2]

    profile = (
        supabase.table("user_bias_profiles")
        .select("bias_scores,archetype,dominant_category")
        .eq("user_id", user_id)
        .execute()
    )
    bias_fingerprint: dict = profile.data[0] if profile.data else {}

    journal_rows = (
        supabase.table("journal_entries")
        .select("themes")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(5)
        .execute()
    )
    seen: set = set()
    journal_themes: list[str] = []
    for row in journal_rows.data or []:
        for t in (row.get("themes") or []):
            if t not in seen:
                seen.add(t)
                journal_themes.append(t)
    journal_themes = journal_themes[:5]

    _USER_CTX_CACHE[user_id] = (time.monotonic(), bias_fingerprint, journal_themes)
    return bias_fingerprint, journal_themes


def _upsert_conversation(
    supabase,
    user_id: str,
    conversation_id: str | None,
    user_message: str,
    assistant_response: str,
) -> str | None:
    """Persist the turn to ai_conversations.

    Option B: one row per session.
    - If conversation_id is provided and the row exists, append to its messages.
    - If conversation_id is provided but the row is new, INSERT with that UUID.
    - If no conversation_id, INSERT a new row (legacy / unauthenticated path).
    Returns the conversation_id used (or None on failure).
    """
    new_msgs = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_response},
    ]
    try:
        if conversation_id:
            existing = (
                supabase.table("ai_conversations")
                .select("messages")
                .eq("id", conversation_id)
                .eq("user_id", user_id)
                .execute()
            )
            if existing.data:
                all_msgs = (existing.data[0]["messages"] or []) + new_msgs
                supabase.table("ai_conversations").update(
                    {"messages": all_msgs, "updated_at": "now()"}
                ).eq("id", conversation_id).execute()
            else:
                supabase.table("ai_conversations").insert(
                    {
                        "id": conversation_id,
                        "user_id": user_id,
                        "messages": new_msgs,
                    }
                ).execute()
            return conversation_id
        else:
            result = supabase.table("ai_conversations").insert(
                {"user_id": user_id, "messages": new_msgs}
            ).execute()
            return result.data[0]["id"] if result.data else None
    except Exception as exc:
        logger.error(f"[AI] _upsert_conversation error: {exc}")
        return None


def _fetch_conversation_messages(supabase, conversation_id: str, user_id: str) -> list[dict]:
    """Return all messages for a session (for episode summarisation)."""
    try:
        res = (
            supabase.table("ai_conversations")
            .select("messages")
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
        return res.data[0]["messages"] if res.data else []
    except Exception:
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Chat endpoint
# ──────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@router.post("/chat")
async def chat(data: ChatRequest, authorization: str | None = Header(None)):
    """Stream an AI Guide response via Server-Sent Events.

    Each SSE chunk is:  data: {"chunk": "..."}\n\n
    Sources event:      data: {"sources": [...]}\n\n
    The stream ends with: data: [DONE]\n\n
    """
    safety_result = safety.check_input(data.message)
    if safety_result.action == "REDIRECT":
        return JSONResponse(
            status_code=422,
            content={"response": safety_result.message, "type": "crisis"},
        )

    user_id = get_user_id(authorization)
    supabase = get_supabase()

    # Tier-3 working context (fast in-memory cache)
    bias_fingerprint, journal_themes = _get_user_context(user_id, supabase)

    # Tier-1/2 memory retrieval (decay-weighted pgvector search)
    memory_ctx = await memory_service.retrieve_memory(user_id, data.message, top_k=3)

    # RAG knowledge retrieval
    rag_context, sources = await rag_query(data.message)

    async def generate():
        full_response = ""
        try:
            async for chunk in stream_response(
                data.message,
                rag_context=rag_context,
                bias_fingerprint=bias_fingerprint,
                journal_themes=journal_themes,
                memory_context=memory_ctx,
            ):
                if safety.check_output(chunk):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            if sources:
                yield f"data: {json.dumps({'sources': sources})}\n\n"

        except Exception as exc:
            logger.error(f"Streaming error: {exc}")
            yield f"data: {json.dumps({'error': 'Stream interrupted'})}\n\n"
        finally:
            # Persist conversation (Option B: one row per session)
            conv_id = _upsert_conversation(
                supabase, user_id, data.conversation_id, data.message, full_response
            )

            # Async badge check
            try:
                await check_and_award_badges(user_id, supabase)
            except Exception as exc:
                logger.error(f"Badge check error: {exc}")

            # Save/update episodic memory in the background (non-blocking)
            if conv_id and full_response:
                all_msgs = _fetch_conversation_messages(supabase, conv_id, user_id)
                if all_msgs:
                    asyncio.create_task(
                        memory_service.save_episode(user_id, conv_id, all_msgs)
                    )

            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/chat/history")
async def chat_history(authorization: str | None = Header(None)):
    """Return the user's past AI Guide conversations, newest first."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("ai_conversations")
        .select("id,messages,created_at,context_summary")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    return result.data or []


# ──────────────────────────────────────────────────────────────────────────────
# Memory panel endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/memory")
async def get_memory(authorization: str | None = Header(None)):
    """Return the user's readable memory state (episodes + facts)."""
    user_id = get_user_id(authorization)
    return await memory_service.get_user_memory(user_id)


@router.delete("/memory/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory_item(
    item_id: str,
    source: str = Query(..., pattern="^(episode|fact)$"),
    authorization: str | None = Header(None),
):
    """Delete a single memory episode or fact."""
    user_id = get_user_id(authorization)
    deleted = await memory_service.delete_memory_item(user_id, item_id, source)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory item not found")


@router.delete("/memory", status_code=status.HTTP_204_NO_CONTENT)
async def wipe_memory(authorization: str | None = Header(None)):
    """GDPR wipe — delete all memory (episodes + facts) for the authenticated user."""
    user_id = get_user_id(authorization)
    await memory_service.wipe_user_memory(user_id)

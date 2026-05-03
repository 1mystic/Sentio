from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.safety import safety
from services.claude_service import stream_response
from services.rag_service import rag_query
from services.supabase_client import get_supabase
from routers._auth_helpers import get_user_id
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@router.post("/chat")
async def chat(data: ChatRequest, authorization: str | None = Header(None)):
    """Stream an AI Guide response via Server-Sent Events.

    The endpoint:
    1. Checks the user's message for crisis signals.
    2. Loads the user's bias fingerprint for personalised context.
    3. Runs RAG retrieval to inject relevant knowledge articles.
    4. Streams Claude's response token-by-token as SSE chunks.
    5. Emits a sources event after the stream if RAG returned citations.
    6. Persists the conversation to ai_conversations after completion.

    Each SSE chunk is:  data: {"chunk": "..."}\n\n
    Sources event:      data: {"sources": [...]}\n\n
    The stream ends with: data: [DONE]\n\n
    """
    # Safety gate
    safety_result = safety.check_input(data.message)
    if safety_result.action == "REDIRECT":
        # Return a plain JSON response (not streaming) for crisis redirection
        return {"response": safety_result.message, "type": "crisis"}

    user_id = get_user_id(authorization)
    supabase = get_supabase()

    # Load user context for personalisation
    profile = (
        supabase.table("user_bias_profiles")
        .select("bias_scores,archetype,dominant_category")
        .eq("user_id", user_id)
        .execute()
    )
    bias_fingerprint: dict = profile.data[0] if profile.data else {}

    # Fetch recent journal themes
    journal_rows = (
        supabase.table("journal_entries")
        .select("themes")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(5)
        .execute()
    )
    journal_themes: list[str] = []
    for row in journal_rows.data or []:
        journal_themes.extend(row.get("themes") or [])
    # Deduplicate while preserving order
    seen: set = set()
    deduped_themes: list[str] = []
    for t in journal_themes:
        if t not in seen:
            seen.add(t)
            deduped_themes.append(t)
    journal_themes = deduped_themes[:5]

    # RAG retrieval — get relevant knowledge articles
    rag_context, sources = await rag_query(data.message)

    async def generate():
        full_response = ""
        try:
            async for chunk in stream_response(
                data.message,
                rag_context=rag_context,
                bias_fingerprint=bias_fingerprint,
                journal_themes=journal_themes,
            ):
                if safety.check_output(chunk):
                    full_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Emit sources after the main stream completes
            if sources:
                yield f"data: {json.dumps({'sources': sources})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': 'Stream interrupted'})}\n\n"
        finally:
            # Persist conversation regardless of whether it completed cleanly
            try:
                supabase.table("ai_conversations").insert(
                    {
                        "user_id": user_id,
                        "messages": [
                            {"role": "user", "content": data.message},
                            {"role": "assistant", "content": full_response},
                        ],
                    }
                ).execute()
            except Exception as e:
                logger.error(f"Failed to persist conversation: {e}")
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

"""Socratic dialogue engine — ported from Episteme (CBC Hackathon 2026).
Implements the 7-algorithm pipeline as FastAPI SSE endpoints.
"""

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from services.safety import safety
from services.claude_service import stream_socratic_response, generate_socratic_insight_card
from services.supabase_client import get_supabase
from routers._auth_helpers import get_user_id
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request schemas ────────────────────────────────────────────────────────────

class CreateSessionRequest(BaseModel):
    domain: str = "general"


class SocraticChatRequest(BaseModel):
    session_id: str
    message: str
    turn_number: int
    domain: str
    conversation_history: list[dict]
    concepts_covered: list[str] = []
    # Algorithm outputs computed client-side (RDSE, SDSM, CBKT-CS)
    quality_score: float = 0.5
    confusion_count: int = 0
    depth_level: str = "CONCEPTUAL"
    next_state: str = "PROBE"
    semantic_accuracy: float = 0.5
    bkt_pl: float = 0.20
    clarity_score: int = 20
    misconception: Optional[str] = None


class InsightRequest(BaseModel):
    session_id: str
    concept: str
    domain: str
    conversation_history: list[dict]


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/session")
async def create_session(
    req: CreateSessionRequest,
    authorization: Optional[str] = Header(None),
):
    """Create a new Socratic session."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    result = supabase.table("socratic_sessions").insert({
        "domain": req.domain,
        "user_id": user_id,
        "turns_count": 0,
        "is_complete": False,
    }).execute()

    if not result.data:
        raise HTTPException(500, "Failed to create session")

    return {"session": result.data[0]}


@router.post("/chat")
async def socratic_chat(
    req: SocraticChatRequest,
    authorization: Optional[str] = Header(None),
):
    """Stream a Socratic response via SSE.

    SSE format:
      data: {"text": "..."}\n\n   — streamed token chunks
      data: {"done": true, "clarity_score": N, "next_state": "..."}\n\n  — final signal
    """
    # Safety gate (crisis detection)
    safety_result = safety.check_input(req.message)
    if safety_result.action == "REDIRECT":
        return JSONResponse(
            status_code=422,
            content={"response": safety_result.message, "type": "crisis"},
        )

    user_id = get_user_id(authorization)
    supabase = get_supabase()

    # Fetch user's bias profile and journal themes for context enrichment
    bias_scores: dict = {}
    journal_themes: list[str] = []
    try:
        profile = supabase.table("user_bias_profiles")\
            .select("bias_scores")\
            .eq("user_id", user_id)\
            .execute()
        if profile.data:
            bias_scores = profile.data[0].get("bias_scores") or {}

        journal_rows = supabase.table("journal_entries")\
            .select("themes")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()
        seen: set = set()
        for row in journal_rows.data or []:
            for t in (row.get("themes") or []):
                if t not in seen:
                    seen.add(t)
                    journal_themes.append(t)
        journal_themes = journal_themes[:5]
    except Exception as e:
        logger.warning(f"Could not fetch user context: {e}")

    async def event_stream():
        full_response = ""
        try:
            async for chunk in stream_socratic_response(
                message=req.message,
                conversation_history=req.conversation_history,
                domain=req.domain,
                next_state=req.next_state,
                quality_score=req.quality_score,
                misconception=req.misconception,
                clarity_score=req.clarity_score,
                bias_scores=bias_scores,
                journal_themes=journal_themes,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'text': chunk})}\n\n"

            yield f"data: {json.dumps({'done': True, 'clarity_score': req.clarity_score, 'next_state': req.next_state, 'can_generate_insight': req.turn_number >= 3})}\n\n"

        except Exception as e:
            logger.error(f"Socratic stream error: {e}")
            yield f"data: {json.dumps({'text': 'I ran into an issue. Please try again.'})}\n\n"
            yield f"data: {json.dumps({'done': True, 'clarity_score': req.clarity_score, 'next_state': req.next_state, 'can_generate_insight': False})}\n\n"
        finally:
            # Persist messages and update session turns_count
            try:
                supabase.table("socratic_messages").insert([
                    {
                        "session_id": req.session_id,
                        "role": "user",
                        "content": req.message,
                        "turn_number": req.turn_number,
                        "algo_state": req.next_state,
                        "clarity_score": req.clarity_score,
                    },
                    {
                        "session_id": req.session_id,
                        "role": "assistant",
                        "content": full_response,
                        "turn_number": req.turn_number,
                        "algo_state": req.next_state,
                        "clarity_score": req.clarity_score,
                    },
                ]).execute()

                supabase.table("socratic_sessions")\
                    .update({"turns_count": req.turn_number + 1})\
                    .eq("id", req.session_id)\
                    .execute()
            except Exception as e:
                logger.error(f"Failed to persist socratic messages: {e}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/sessions")
async def list_sessions(authorization: Optional[str] = Header(None)):
    """List the user's past Socratic sessions, newest first, with a preview of the first user message."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    result = supabase.table("socratic_sessions")\
        .select("id,domain,turns_count,is_complete,created_at")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .limit(20)\
        .execute()

    sessions = result.data or []

    # Batch-fetch first user message per session as a preview
    enriched = []
    for session in sessions:
        preview = ""
        try:
            preview_result = supabase.table("socratic_messages")\
                .select("content")\
                .eq("session_id", session["id"])\
                .eq("role", "user")\
                .order("turn_number")\
                .limit(1)\
                .execute()
            if preview_result.data:
                preview = preview_result.data[0]["content"][:100]
        except Exception:
            pass
        enriched.append({**session, "preview": preview})

    return {"sessions": enriched}


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    authorization: Optional[str] = Header(None),
):
    """Return all messages and the insight card for a past Socratic session."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    session_result = supabase.table("socratic_sessions")\
        .select("*")\
        .eq("id", session_id)\
        .eq("user_id", user_id)\
        .execute()

    if not session_result.data:
        raise HTTPException(404, "Session not found")

    session = session_result.data[0]

    messages_result = supabase.table("socratic_messages")\
        .select("*")\
        .eq("session_id", session_id)\
        .order("turn_number")\
        .execute()

    insight_result = supabase.table("socratic_insight_cards")\
        .select("*")\
        .eq("session_id", session_id)\
        .limit(1)\
        .execute()

    return {
        "session": session,
        "messages": messages_result.data or [],
        "insight_card": insight_result.data[0] if insight_result.data else None,
    }


@router.post("/insights")
async def generate_insight(
    req: InsightRequest,
    authorization: Optional[str] = Header(None),
):
    """Generate an insight card after ≥4 user turns."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    user_turns = [m for m in req.conversation_history if m.get("role") == "user"]
    if len(user_turns) < 3:
        raise HTTPException(400, "Need at least 3 user turns to generate an insight card")

    try:
        insight = await generate_socratic_insight_card(
            conversation_history=req.conversation_history,
            concept=req.concept,
            domain=req.domain,
        )
    except Exception as e:
        logger.error(f"Insight generation error: {e}")
        raise HTTPException(500, f"Failed to generate insight: {e}")

    # Persist insight card
    try:
        supabase.table("socratic_insight_cards").insert({
            "session_id": req.session_id,
            "concept": insight.get("concept", req.concept),
            "insight": insight.get("insight", ""),
            "gaps": insight.get("gaps", []),
            "clarity_score": insight.get("clarity_score", 0),
            "next_question": insight.get("next_question", ""),
        }).execute()

        supabase.table("socratic_sessions")\
            .update({"is_complete": True})\
            .eq("id", req.session_id)\
            .execute()
    except Exception as e:
        logger.error(f"Failed to persist insight card: {e}")

    return {"insight_card": insight}

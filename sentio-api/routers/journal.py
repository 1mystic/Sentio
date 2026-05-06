from fastapi import APIRouter, HTTPException, BackgroundTasks, Header, Query, status
from pydantic import BaseModel
from services.supabase_client import get_supabase
from services.bias_classifier import classify_biases
from services.journal_nlp import analyze_journal
from services.safety import safety
from services.badge_engine import check_and_award_badges
from routers._auth_helpers import get_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class JournalCreate(BaseModel):
    content: str
    prompt_used: str | None = None


class JournalUpdate(BaseModel):
    content: str | None = None
    prompt_used: str | None = None


# ---------------------------------------------------------------------------
# Background processing
# ---------------------------------------------------------------------------

async def _process_entry(entry_id: str, content: str, user_id: str) -> None:
    """Background task: run bias classification + NLP, persist results, check badges."""
    try:
        biases, nlp = await classify_biases(content), await analyze_journal(content)
        supabase = get_supabase()
        supabase.table("journal_entries").update(
            {
                "detected_biases": biases,
                "themes": nlp.get("themes", []),
                "sentiment_score": nlp.get("sentiment_score", 0.0),
            }
        ).eq("id", entry_id).execute()

        if biases:
            _update_bias_profile(user_id, biases)

        await check_and_award_badges(user_id, supabase)
    except Exception as e:
        logger.error(f"Background entry processing error (entry={entry_id}): {e}")


_ARCHETYPE_MAP = {
    'confirmation_bias':  'The Conviction Keeper',
    'anchoring_bias':     'The Anchor',
    'availability_bias':  'The Storyteller',
    'overconfidence':     'The Visionary',
    'social_conformity':  'The Harmonizer',
    'attribution_error':  'The Judge',
    'sunk_cost_fallacy':  'The Investor',
    'dunning_kruger':     'The Explorer',
    'status_quo_bias':    'The Traditionalist',
    'halo_effect':        'The Idealist',
    'bandwagon_effect':   'The Follower',
    'recency_bias':       'The Moment-Chaser',
}

def _compute_archetype(bias_scores: dict) -> str | None:
    if not bias_scores:
        return None
    top = max(bias_scores, key=lambda k: bias_scores[k])
    return _ARCHETYPE_MAP.get(top, 'The Thinker')


def _update_bias_profile(user_id: str, biases: list[dict]) -> None:
    """Incrementally update the user's bias_scores in user_bias_profiles."""
    supabase = get_supabase()
    profile = (
        supabase.table("user_bias_profiles")
        .select("bias_scores")
        .eq("user_id", user_id)
        .execute()
    )
    scores: dict = profile.data[0]["bias_scores"] if profile.data else {}

    for b in biases:
        bias_id = b.get("bias_id") or b.get("bias")
        if bias_id:
            delta = b.get("confidence", 0.5) * 0.1
            scores[bias_id] = min(1.0, scores.get(bias_id, 0.0) + delta)

    archetype = _compute_archetype(scores)
    supabase.table("user_bias_profiles").upsert(
        {"user_id": user_id, "bias_scores": scores, "archetype": archetype}
    ).execute()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_entry(
    data: JournalCreate,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(None),
):
    """Create a journal entry.

    Immediately saves the raw content, then triggers an async background
    task to run the bias classifier and NLP pipeline.

    If crisis keywords are detected the entry is NOT saved and the user
    receives crisis resource information instead.
    """
    # Safety gate — must run BEFORE any persistence
    safety_result = safety.check_input(data.content)
    if safety_result.action == "REDIRECT":
        return {"crisis_resources": safety_result.message, "entry_saved": False}

    user_id = get_user_id(authorization)
    supabase = get_supabase()

    result = supabase.table("journal_entries").insert(
        {
            "user_id": user_id,
            "content": data.content,
            "prompt_used": data.prompt_used,
        }
    ).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save journal entry",
        )

    entry = result.data[0]
    background_tasks.add_task(_process_entry, entry["id"], data.content, user_id)
    return entry


@router.get("/")
async def list_entries(
    authorization: str | None = Header(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Return the authenticated user's journal entries, newest first."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("journal_entries")
        .select("id,created_at,content,prompt_used,sentiment_score,themes,detected_biases")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return result.data or []


@router.get("/themes")
async def aggregate_themes(authorization: str | None = Header(None)):
    """Return the user's top themes aggregated across all journal entries."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("journal_entries")
        .select("themes")
        .eq("user_id", user_id)
        .execute()
    )
    from collections import Counter
    all_themes: list[str] = []
    for row in (result.data or []):
        all_themes.extend(row.get("themes") or [])
    top = [{"theme": t, "count": c} for t, c in Counter(all_themes).most_common(10)]
    return top


@router.post("/{entry_id}/reflections")
async def generate_reflections(entry_id: str, authorization: str | None = Header(None)):
    """Generate 3 Claude-powered reflection questions for a journal entry."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    result = (
        supabase.table("journal_entries")
        .select("content,detected_biases")
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    entry = result.data
    from services.claude_service import generate_journal_reflections
    questions = await generate_journal_reflections(
        entry["content"],
        entry.get("detected_biases") or [],
    )
    return {"questions": questions, "entry_id": entry_id}


@router.get("/{entry_id}")
async def get_entry(entry_id: str, authorization: str | None = Header(None)):
    """Return a single journal entry belonging to the authenticated user."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("journal_entries")
        .select("*")
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return result.data


@router.patch("/{entry_id}")
async def update_entry(
    entry_id: str,
    data: JournalUpdate,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(None),
):
    """Update content of an existing journal entry and re-run NLP pipeline."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    update_payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_payload:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields to update",
        )

    if "content" in update_payload:
        safety_result = safety.check_input(update_payload["content"])
        if safety_result.action == "REDIRECT":
            return {"crisis_resources": safety_result.message, "entry_saved": False}

    result = (
        supabase.table("journal_entries")
        .update(update_payload)
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    entry = result.data[0]
    if "content" in update_payload:
        background_tasks.add_task(
            _process_entry, entry_id, update_payload["content"], user_id
        )
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(entry_id: str, authorization: str | None = Header(None)):
    """Permanently delete a journal entry."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("journal_entries")
        .delete()
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")


@router.get("/{entry_id}/insights")
async def get_entry_insights(entry_id: str, authorization: str | None = Header(None)):
    """Return the NLP analysis for a specific journal entry."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("journal_entries")
        .select("detected_biases,themes,sentiment_score")
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return result.data

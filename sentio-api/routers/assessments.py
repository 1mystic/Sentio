from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from services.supabase_client import get_supabase
from routers._auth_helpers import get_user_id
from routers.journal import _compute_archetype
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class SubmitRequest(BaseModel):
    raw_scores: dict
    computed_scores: dict
    bias_implications: dict | None = None


@router.get("/")
async def list_assessments():
    """Return all available assessments (public — no auth required)."""
    supabase = get_supabase()
    result = supabase.table("assessments").select(
        "id,slug,title,description,estimated_minutes,validated_tool"
    ).execute()
    return result.data or []


@router.get("/user/results")
async def user_assessment_results(authorization: str | None = Header(None)):
    """Return the most recent result per assessment for the current user."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("assessment_results")
        .select("assessment_id, computed_scores, completed_at")
        .eq("user_id", user_id)
        .order("completed_at", desc=True)
        .execute()
    )
    seen: dict = {}
    for row in (result.data or []):
        aid = row["assessment_id"]
        if aid not in seen:
            seen[aid] = row
    return list(seen.values())


@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Return full assessment details including questions."""
    supabase = get_supabase()
    result = (
        supabase.table("assessments")
        .select("*")
        .eq("id", assessment_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found"
        )
    return result.data


@router.post("/{assessment_id}/submit", status_code=status.HTTP_201_CREATED)
async def submit_assessment(
    assessment_id: str,
    data: SubmitRequest,
    authorization: str | None = Header(None),
):
    """Submit assessment results and store them for the authenticated user."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    # Verify the assessment exists
    check = (
        supabase.table("assessments")
        .select("id")
        .eq("id", assessment_id)
        .single()
        .execute()
    )
    if not check.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found"
        )

    result = supabase.table("assessment_results").insert(
        {
            "user_id": user_id,
            "assessment_id": assessment_id,
            "raw_scores": data.raw_scores,
            "computed_scores": data.computed_scores,
            "bias_implications": data.bias_implications,
        }
    ).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save assessment results",
        )

    # Update user_bias_profiles from assessment results
    try:
        assessment_resp = supabase.table("assessments").select("questions").eq(
            "id", assessment_id
        ).single().execute()
        questions = (assessment_resp.data or {}).get("questions", [])

        # Build question_id → bias_signal map
        signal_map = {str(q.get("id", "")): q["bias_signal"]
                      for q in questions if q.get("bias_signal") and q.get("id")}

        # Accumulate raw scores per bias_signal (likert 1–5)
        totals: dict[str, float] = {}
        counts: dict[str, int] = {}
        for q_id, score in data.raw_scores.items():
            signal = signal_map.get(str(q_id))
            if signal:
                totals[signal] = totals.get(signal, 0.0) + float(score)
                counts[signal] = counts.get(signal, 0) + 1

        # Normalize to 0–1  (likert5: 1=min, 5=max → (score-1)/4)
        new_scores = {sig: round((totals[sig] / counts[sig] - 1) / 4, 3) for sig in totals}

        if new_scores:
            existing = supabase.table("user_bias_profiles").select(
                "bias_scores"
            ).eq("user_id", user_id).execute()
            current = (existing.data[0]["bias_scores"] or {}) if existing.data else {}

            merged = dict(current)
            for bias_id, score in new_scores.items():
                prev = current.get(bias_id, 0.0)
                # Blend: existing journal score (60%) + assessment (40%); or just assessment if new
                merged[bias_id] = round(prev * 0.6 + score * 0.4, 3) if prev else score

            archetype = _compute_archetype(merged)
            if existing.data:
                supabase.table("user_bias_profiles").update(
                    {"bias_scores": merged, "archetype": archetype}
                ).eq("user_id", user_id).execute()
            else:
                supabase.table("user_bias_profiles").insert(
                    {"user_id": user_id, "bias_scores": merged, "archetype": archetype}
                ).execute()
    except Exception as e:
        logger.warning(f"Bias profile update after assessment failed (non-blocking): {e}")

    return result.data[0]


@router.get("/{assessment_id}/history")
async def assessment_history(
    assessment_id: str, authorization: str | None = Header(None)
):
    """Return all past submissions for this assessment by the current user."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("assessment_results")
        .select("*")
        .eq("user_id", user_id)
        .eq("assessment_id", assessment_id)
        .order("completed_at", desc=True)
        .execute()
    )
    return result.data or []

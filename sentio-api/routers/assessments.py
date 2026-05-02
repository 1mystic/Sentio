from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from services.supabase_client import get_supabase
from routers._auth_helpers import get_user_id
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

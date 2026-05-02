from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from services.supabase_client import get_supabase
from routers._auth_helpers import get_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    preferences: dict | None = None
    cognitive_style: dict | None = None
    onboarding_completed: bool | None = None


@router.get("/me")
async def get_me(authorization: str | None = Header(None)):
    """Return the authenticated user's profile row."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    )
    return result.data or {}


@router.patch("/me")
async def update_me(
    data: ProfileUpdate, authorization: str | None = Header(None)
):
    """Partially update the authenticated user's profile."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    update_payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_payload:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fields provided for update",
        )

    result = (
        supabase.table("profiles")
        .update(update_payload)
        .eq("id", user_id)
        .execute()
    )
    return result.data[0] if result.data else {}


@router.get("/me/bias-profile")
async def get_bias_profile(authorization: str | None = Header(None)):
    """Return the user's current bias fingerprint."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("user_bias_profiles")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else {"bias_scores": {}, "archetype": None}

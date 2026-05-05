from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.supabase_client import get_supabase
from routers._auth_helpers import get_user_id
import logging
import json

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


@router.get("/me/export")
async def export_user_data(authorization: str | None = Header(None)):
    """Export all data for the authenticated user as a JSON download."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    profile = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    journal = supabase.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    assessments = supabase.table("assessment_results").select("*").eq("user_id", user_id).order("completed_at", desc=True).execute()
    bias_profile = supabase.table("user_bias_profiles").select("*").eq("user_id", user_id).execute()

    payload = {
        "profile": profile.data or {},
        "journal_entries": journal.data or [],
        "assessment_results": assessments.data or [],
        "bias_profile": bias_profile.data[0] if bias_profile.data else {},
    }

    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": "attachment; filename=sentio-data-export.json"},
    )


@router.get("/me/notifications")
async def get_notifications(authorization: str | None = Header(None)):
    """Return smart notifications derived from user activity data."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    notifs = []

    # Journal streak check
    entries = supabase.table("journal_entries").select("created_at").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
    entry_list = entries.data or []
    if not entry_list:
        notifs.append({"id": "tip-journal", "type": "insight", "title": "Start your journal", "message": "Write your first entry to unlock AI bias detection and weekly insights.", "read": False, "created_at": __import__('datetime').datetime.utcnow().isoformat(), "link": "/journal/new"})
    else:
        from datetime import datetime, timezone, timedelta
        latest = datetime.fromisoformat(entry_list[0]["created_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) - latest > timedelta(hours=36):
            notifs.append({"id": "journal-nudge", "type": "insight", "title": "Time to reflect", "message": f"Your last journal entry was {(datetime.now(timezone.utc) - latest).days + 1} day(s) ago. Keep your streak alive!", "read": False, "created_at": __import__('datetime').datetime.utcnow().isoformat(), "link": "/journal/new"})

    # Assessment completion check
    completed = supabase.table("assessment_results").select("assessment_id").eq("user_id", user_id).execute()
    all_assessments = supabase.table("assessments").select("id,title").execute()
    completed_ids = {r["assessment_id"] for r in (completed.data or [])}
    pending = [a for a in (all_assessments.data or []) if a["id"] not in completed_ids]
    if pending:
        a = pending[0]
        notifs.append({"id": f"assess-{a['id']}", "type": "assessment", "title": "Assessment available", "message": f"'{a['title']}' is ready to take. Discover your cognitive patterns.", "read": False, "created_at": __import__('datetime').datetime.utcnow().isoformat(), "link": f"/assessments/{a['id']}"})

    # Bias profile insight
    bp = supabase.table("user_bias_profiles").select("archetype,bias_scores").eq("user_id", user_id).execute()
    if bp.data and bp.data[0].get("archetype"):
        notifs.append({"id": "archetype-ready", "type": "insight", "title": "Your archetype is set", "message": f"You are '{bp.data[0]['archetype']}'. View your full profile on the dashboard.", "read": True, "created_at": __import__('datetime').datetime.utcnow().isoformat(), "link": "/dashboard"})

    return notifs


@router.post("/me/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notifications_read(authorization: str | None = Header(None)):
    """Mark all notifications as read (stored client-side; endpoint is a no-op stub)."""
    get_user_id(authorization)  # validates auth


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(authorization: str | None = Header(None)):
    """Permanently delete the authenticated user's account and all associated data."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    # Delete user data in dependency order
    supabase.table("user_bias_profiles").delete().eq("user_id", user_id).execute()
    supabase.table("journal_entries").delete().eq("user_id", user_id).execute()
    supabase.table("assessment_results").delete().eq("user_id", user_id).execute()
    supabase.table("ai_conversations").delete().eq("user_id", user_id).execute()
    supabase.table("therapist_bookings").delete().eq("user_id", user_id).execute()
    supabase.table("profiles").delete().eq("id", user_id).execute()

    # Delete the Supabase auth user (requires service-role key)
    try:
        supabase.auth.admin.delete_user(user_id)
    except Exception as e:
        logger.warning(f"Could not delete auth user {user_id}: {e}")

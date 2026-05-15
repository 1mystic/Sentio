from fastapi import APIRouter, Header, HTTPException, Query, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from services.supabase_client import get_supabase
from routers._auth_helpers import get_user, get_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class BookingRequest(BaseModel):
    message: str | None = None
    requested_at: str | None = None  # ISO 8601 datetime string


@router.get("/")
async def list_therapists(
    language: Optional[str] = Query(None, description="Filter by language, e.g. 'Hindi'"),
    specialization: Optional[str] = Query(None, description="Filter by specialization keyword"),
    format_type: Optional[str] = Query(
        None, alias="format", description="Filter by session format: online/in-person/both"
    ),
    lat: Optional[float] = Query(None, description="User latitude for nearest-first ordering"),
    lng: Optional[float] = Query(None, description="User longitude for nearest-first ordering"),
    radius_km: float = Query(50, description="Radius in km when lat/lng provided"),
):
    """Return verified therapists. Supports language/specialization/format filters.
    When lat+lng are provided, returns therapists nearest to that location first
    (those without coordinates are appended at the end).
    """
    supabase = get_supabase()

    if lat is not None and lng is not None:
        # Use the haversine RPC for nearest therapists
        try:
            result = supabase.rpc(
                "get_nearest_therapists",
                {"user_lat": lat, "user_lng": lng, "radius_km": radius_km, "max_rows": 100},
            ).execute()
            therapists: list[dict] = result.data or []
        except Exception:
            # Fallback to full list if RPC not installed
            result = supabase.table("therapists").select("*").eq("verified", True).execute()
            therapists = result.data or []
    else:
        result = supabase.table("therapists").select("*").eq("verified", True).execute()
        therapists = result.data or []

    # Normalise session_format to a lowercase string for filtering
    def get_format(t: dict) -> str:
        return (t.get("session_format") or "").lower()

    if language:
        therapists = [
            t for t in therapists
            if language.lower() in [lang.lower() for lang in (t.get("languages") or [])]
        ]
    if specialization:
        therapists = [
            t for t in therapists
            if specialization.lower() in [s.lower() for s in (t.get("specializations") or [])]
        ]
    if format_type:
        norm = format_type.lower()
        therapists = [
            t for t in therapists
            if norm in get_format(t) or get_format(t) in norm
        ]

    return therapists


@router.get("/{therapist_id}")
async def get_therapist(therapist_id: str):
    """Return a single therapist's full profile."""
    supabase = get_supabase()
    result = (
        supabase.table("therapists")
        .select("*")
        .eq("id", therapist_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Therapist not found"
        )
    return result.data


@router.post("/{therapist_id}/book", status_code=status.HTTP_201_CREATED)
async def request_connection(
    therapist_id: str,
    data: BookingRequest,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(None),
):
    """Submit a connection request to a therapist.

    Sentio does not intermediate the clinical relationship — this records
    the user's intent; actual booking happens on the therapist's source platform.
    """
    user = get_user(authorization)
    user_id = user["id"]
    user_email = user.get("email")
    supabase = get_supabase()

    check = (
        supabase.table("therapists")
        .select("id,verified,name")
        .eq("id", therapist_id)
        .single()
        .execute()
    )
    if not check.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Therapist not found"
        )
    if not check.data.get("verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This therapist is not currently accepting connection requests",
        )

    result = supabase.table("bookings").insert(
        {
            "user_id": user_id,
            "therapist_id": therapist_id,
            "message": data.message,
            "requested_at": data.requested_at,
            "status": "pending",
        }
    ).execute()

    booking_id = result.data[0]["id"] if result.data else None
    
    if user_email:
        user_profile = supabase.table("profiles").select("display_name").eq("id", user_id).single().execute()
        user_name = user_profile.data.get("display_name") if user_profile.data else "User"
        therapist_name = check.data.get("name", "your therapist")
        
        from services.email_service import send_booking_notification
        background_tasks.add_task(send_booking_notification, user_email, user_name, therapist_name)

    return {"status": "request_submitted", "booking_id": booking_id}


@router.get("/bookings/mine")
async def my_bookings(authorization: str | None = Header(None)):
    """Return all booking requests made by the authenticated user."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("bookings")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []

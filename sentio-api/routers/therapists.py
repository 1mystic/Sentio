from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional
from services.supabase_client import get_supabase
from routers._auth_helpers import get_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class BookingRequest(BaseModel):
    message: str | None = None
    requested_at: str | None = None  # ISO 8601 datetime string


@router.get("/")
async def list_therapists(
    language: Optional[str] = Query(None, description="Filter by language code, e.g. 'en'"),
    specialization: Optional[str] = Query(None, description="Filter by specialization keyword"),
    format_type: Optional[str] = Query(
        None, alias="format", description="Filter by session format: online/in-person/both"
    ),
):
    """Return all verified therapists, with optional preference-based filtering.

    Note: filtering is done in Python after fetching because Supabase PostgREST
    doesn't support native array-contains filtering without custom RPC in all versions.
    """
    supabase = get_supabase()
    result = supabase.table("therapists").select("*").eq("verified", True).execute()
    therapists: list[dict] = result.data or []

    if language:
        therapists = [
            t for t in therapists if language in (t.get("languages") or [])
        ]
    if specialization:
        therapists = [
            t for t in therapists
            if specialization.lower() in [s.lower() for s in (t.get("specializations") or [])]
        ]
    if format_type:
        therapists = [
            t for t in therapists if format_type in (t.get("session_formats") or [])
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
    authorization: str | None = Header(None),
):
    """Submit a connection request to a therapist.

    Sentio does not intermediate the clinical relationship — this simply
    records the user's intent and passes contact details accordingly.
    """
    user_id = get_user_id(authorization)
    supabase = get_supabase()

    # Verify therapist exists and is verified
    check = (
        supabase.table("therapists")
        .select("id,verified")
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

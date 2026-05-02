from fastapi import APIRouter, HTTPException, Query, status
from services.supabase_client import get_supabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def list_biases(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    search: Optional[str] = Query(None, description="Case-insensitive name search"),
):
    """Return all biases, optionally filtered by category or name search."""
    supabase = get_supabase()
    query = supabase.table("biases").select("*").order("name")
    if category:
        query = query.eq("category", category)
    if search:
        query = query.ilike("name", f"%{search}%")
    result = query.execute()
    return result.data or []


@router.get("/categories")
async def list_categories():
    """Return the distinct bias categories available."""
    return [
        {"slug": "memory", "label": "Memory"},
        {"slug": "social", "label": "Social"},
        {"slug": "decision", "label": "Decision-Making"},
        {"slug": "self", "label": "Self-Perception"},
        {"slug": "belief", "label": "Belief"},
        {"slug": "reasoning", "label": "Reasoning"},
    ]


@router.get("/{slug}")
async def get_bias(slug: str):
    """Return a single bias by its URL slug."""
    supabase = get_supabase()
    result = (
        supabase.table("biases").select("*").eq("slug", slug).single().execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bias not found"
        )
    return result.data

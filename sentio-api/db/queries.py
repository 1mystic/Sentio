"""Reusable optimised Supabase query helpers."""
from services.supabase_client import get_supabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_user_bias_profile(user_id: str) -> dict:
    """Fetch user bias profile or return empty defaults."""
    try:
        result = (
            get_supabase()
            .table("user_bias_profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception as e:
        logger.error(f"get_user_bias_profile error: {e}")
    return {"bias_scores": {}, "archetype": None, "dominant_category": None, "confidence": 0.0}


def get_recent_journal_themes(user_id: str, limit: int = 5) -> list[str]:
    """Return deduplicated list of recent journal themes."""
    try:
        rows = (
            get_supabase()
            .table("journal_entries")
            .select("themes")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        seen = set()
        themes = []
        for row in (rows.data or []):
            for t in (row.get("themes") or []):
                if t not in seen:
                    seen.add(t)
                    themes.append(t)
        return themes[:10]
    except Exception as e:
        logger.error(f"get_recent_journal_themes error: {e}")
        return []


def get_journal_entry_count(user_id: str) -> int:
    try:
        result = (
            get_supabase()
            .table("journal_entries")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .execute()
        )
        return result.count or 0
    except Exception:
        return 0


def get_completed_assessment_ids(user_id: str) -> list[str]:
    try:
        result = (
            get_supabase()
            .table("assessment_results")
            .select("assessment_id")
            .eq("user_id", user_id)
            .execute()
        )
        return [r["assessment_id"] for r in (result.data or [])]
    except Exception:
        return []


def upsert_bias_profile(user_id: str, bias_scores: dict, category_scores: Optional[dict] = None) -> None:
    """Upsert user bias profile. Compute dominant_category from category_scores."""
    try:
        payload: dict = {"user_id": user_id, "bias_scores": bias_scores}
        if category_scores:
            payload["category_scores"] = category_scores
            dominant = max(category_scores, key=lambda k: category_scores[k], default=None)
            payload["dominant_category"] = dominant
        payload["last_updated"] = "NOW()"
        get_supabase().table("user_bias_profiles").upsert(payload, on_conflict="user_id").execute()
    except Exception as e:
        logger.error(f"upsert_bias_profile error: {e}")

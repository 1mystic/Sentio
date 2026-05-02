from collections import Counter
from fastapi import APIRouter, Header
from services.supabase_client import get_supabase
from services.recommender import recommend_bias_to_explore, recommend_assessment
from routers._auth_helpers import get_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/bias-fingerprint")
async def bias_fingerprint(authorization: str | None = Header(None)):
    """Return the user's current bias fingerprint (scores per bias)."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    result = (
        supabase.table("user_bias_profiles")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else {
        "bias_scores": {},
        "archetype": None,
        "dominant_category": None,
        "confidence": None,
    }


@router.get("/recommendations")
async def recommendations(authorization: str | None = Header(None)):
    """Return personalised next-step recommendations."""
    user_id = get_user_id(authorization)
    next_bias = await recommend_bias_to_explore(user_id)
    next_assessment = await recommend_assessment(user_id)
    return {"next_bias": next_bias, "next_assessment": next_assessment}


@router.get("/weekly")
async def weekly_insights(authorization: str | None = Header(None)):
    """Return a short list of narrative insights based on the last 7 entries."""
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    entries = (
        supabase.table("journal_entries")
        .select("detected_biases,themes,sentiment_score,created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(7)
        .execute()
    )

    all_themes: list[str] = []
    all_sentiment: list[float] = []
    all_biases: list[str] = []

    for e in entries.data or []:
        all_themes.extend(e.get("themes") or [])
        if e.get("sentiment_score") is not None:
            all_sentiment.append(e["sentiment_score"])
        for b in e.get("detected_biases") or []:
            bid = b.get("bias_id") or b.get("bias")
            if bid:
                all_biases.append(bid)

    top_themes = [t for t, _ in Counter(all_themes).most_common(3)]
    entry_count = len(entries.data or [])
    avg_sentiment = sum(all_sentiment) / len(all_sentiment) if all_sentiment else None

    insights = []
    if entry_count > 0:
        insights.append({
            "type": "journal",
            "text": f"You've written {entry_count} journal {'entry' if entry_count == 1 else 'entries'} this week.",
            "icon": "edit",
        })
    if top_themes:
        insights.append({
            "type": "themes",
            "text": f"Your recurring themes: {', '.join(top_themes)}.",
            "icon": "tag",
        })
    if avg_sentiment is not None:
        tone = "positive" if avg_sentiment > 0.2 else ("negative" if avg_sentiment < -0.2 else "neutral")
        insights.append({
            "type": "sentiment",
            "text": f"Your entries this week have a generally {tone} emotional tone.",
            "icon": "bar-chart",
        })
    if not insights:
        insights.append({
            "type": "empty",
            "text": "Journal for 7 days to unlock your weekly insights.",
            "icon": "info",
        })

    return insights

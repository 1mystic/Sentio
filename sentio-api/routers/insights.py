from collections import Counter
from fastapi import APIRouter, Header
from services.supabase_client import get_supabase
from services.recommender import recommend_bias_to_explore, recommend_assessment
from routers._auth_helpers import get_user_id
import logging
import json
import os
from datetime import datetime
import anthropic

_WEEKLY_INSIGHT_CACHE: dict[str, list] = {}

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
    """Return Claude-synthesized narrative insights based on the last 7 entries."""
    user_id = get_user_id(authorization)
    
    current_year, current_week, _ = datetime.now().isocalendar()
    cache_key = f"{user_id}_{current_year}_{current_week}"
    
    if cache_key in _WEEKLY_INSIGHT_CACHE:
        return _WEEKLY_INSIGHT_CACHE[cache_key]

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

    entry_count = len(entries.data or [])
    if entry_count == 0:
        return [{
            "type": "empty",
            "text": "Journal for 7 days to unlock your weekly insights.",
            "icon": "info",
        }]

    top_themes = [t for t, _ in Counter(all_themes).most_common(5)]
    top_biases = [b for b, _ in Counter(all_biases).most_common(3)]
    avg_sentiment = sum(all_sentiment) / len(all_sentiment) if all_sentiment else 0.0

    sessions_res = (
        supabase.table("socratic_sessions")
        .select("id")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    session_count = len(sessions_res.data or [])

    synthesis_prompt = f"""
You are analyzing one week of cognitive clarity work for a user.
Based on the following data, write 3 specific, personalized insights.

This week's data:
- Journal entries: {entry_count} entries
- Average sentiment: {avg_sentiment:.2f} (range: -1 negative to +1 positive)
- Recurring themes: {', '.join(top_themes)}
- Most detected biases: {', '.join(top_biases)}
- Socratic sessions completed: {session_count}

Write exactly 3 insights. Each insight must:
1. Reference a specific data point (not generic)
2. Name a pattern the user may not have noticed
3. End with one actionable question for the user to reflect on

Format: JSON array of {{"type": "str", "text": "str", "icon": "str"}}
The "type" must be a short category (e.g., "bias", "sentiment", "pattern").
The "icon" must be a valid lucide-vue-next icon name in lowercase (e.g. "brain", "bar-chart", "lightbulb").
Do not include clinical terms, diagnoses, or treatment recommendations.
"""

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    try:
        response = await client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001"),
            max_tokens=400,
            system="You are a reflective cognitive coach. Output only valid JSON arrays.",
            messages=[{"role": "user", "content": synthesis_prompt}],
        )
        text = response.content[0].text if response.content else "[]"
        clean = text.replace("```json", "").replace("```", "").strip()
        insights = json.loads(clean)
        
        _WEEKLY_INSIGHT_CACHE[cache_key] = insights
        return insights
    except Exception as e:
        logger.error(f"Weekly insight synthesis error: {e}")
        return [{
            "type": "error",
            "text": "Could not generate insights at this time.",
            "icon": "alert-circle"
        }]


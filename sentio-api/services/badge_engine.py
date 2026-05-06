"""
Badge engine: checks all badge conditions for a user and awards newly earned ones.
Call after journal submit, assessment submit, and AI conversation save.
"""
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

BADGE_DEFINITIONS = {
    "first_journal":    {"name": "First Reflection",     "icon": "📝", "description": "Wrote your first journal entry"},
    "streak_7":         {"name": "Week of Clarity",       "icon": "🔥", "description": "7-day journaling streak"},
    "streak_30":        {"name": "Month of Mindfulness",  "icon": "🌙", "description": "30-day journaling streak"},
    "bias_3":           {"name": "Pattern Spotter",       "icon": "🔍", "description": "3 unique biases identified across journal entries"},
    "bias_10":          {"name": "Bias Hunter",           "icon": "🎯", "description": "10 unique biases identified"},
    "no_bias":          {"name": "Clean Slate",           "icon": "✨", "description": "5 journal entries with no dominant bias detected"},
    "assessment_1":     {"name": "Self-Examiner",         "icon": "📊", "description": "Completed first assessment"},
    "assessment_all":   {"name": "Full Spectrum",         "icon": "🌈", "description": "Completed all available assessments"},
    "ai_convo":         {"name": "Deep Thinker",          "icon": "🧠", "description": "First AI Guide conversation"},
    "community_first":  {"name": "Contributor",           "icon": "💬", "description": "First community thread or reply"},
    "community_10":     {"name": "Voice of Reason",       "icon": "🎙️", "description": "10 community contributions"},
    "archetype_set":    {"name": "Self-Aware",            "icon": "🪞", "description": "Cognitive archetype computed"},
}


def _compute_streak(entries: list[dict]) -> int:
    """Return the current consecutive daily journaling streak."""
    if not entries:
        return 0
    days = sorted(
        {date.fromisoformat(e["created_at"][:10]) for e in entries if e.get("created_at")},
        reverse=True,
    )
    if not days:
        return 0
    streak = 1
    for i in range(1, len(days)):
        if days[i - 1] - days[i] == timedelta(days=1):
            streak += 1
        else:
            break
    return streak


async def check_and_award_badges(user_id: str, supabase) -> list[str]:
    """Check all badge conditions, award new ones, return newly awarded badge IDs."""
    try:
        awarded = {
            r["badge_id"]
            for r in (supabase.table("user_badges").select("badge_id").eq("user_id", user_id).execute().data or [])
        }
    except Exception as e:
        logger.error(f"Could not load existing badges for {user_id}: {e}")
        return []

    newly_awarded: list[str] = []

    def award(badge_id: str):
        if badge_id not in awarded:
            try:
                supabase.table("user_badges").insert({"user_id": user_id, "badge_id": badge_id}).execute()
                newly_awarded.append(badge_id)
                awarded.add(badge_id)
                logger.info(f"Awarded badge '{badge_id}' to user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to insert badge '{badge_id}': {e}")

    # Journal entries
    entries = supabase.table("journal_entries").select("id,created_at,detected_biases").eq("user_id", user_id).execute().data or []
    if len(entries) >= 1:
        award("first_journal")

    streak = _compute_streak(entries)
    if streak >= 7:
        award("streak_7")
    if streak >= 30:
        award("streak_30")

    # Unique biases detected across journal
    all_biases: set[str] = set()
    clean_entries = 0
    for e in entries:
        detected = e.get("detected_biases") or []
        if not detected:
            clean_entries += 1
        for b in detected:
            label = b.get("bias_id") or b.get("label") or b.get("slug") or ""
            if label:
                all_biases.add(label)
    all_biases.discard("")
    if len(all_biases) >= 3:
        award("bias_3")
    if len(all_biases) >= 10:
        award("bias_10")
    if clean_entries >= 5:
        award("no_bias")

    # Assessments
    results = supabase.table("assessment_results").select("assessment_id").eq("user_id", user_id).execute().data or []
    total_assessments = supabase.table("assessments").select("id", count="exact").execute().count or 0
    if len(results) >= 1:
        award("assessment_1")
    if total_assessments > 0 and len({r["assessment_id"] for r in results}) >= total_assessments:
        award("assessment_all")

    # AI conversations
    ai_count = supabase.table("ai_conversations").select("id", count="exact").eq("user_id", user_id).execute().count or 0
    if ai_count >= 1:
        award("ai_convo")

    # Community contributions (tables may not exist yet — guard defensively)
    try:
        thread_count = supabase.table("community_threads").select("id", count="exact").eq("author_id", user_id).execute().count or 0
        reply_count = supabase.table("community_replies").select("id", count="exact").eq("author_id", user_id).execute().count or 0
        total_community = thread_count + reply_count
        if total_community >= 1:
            award("community_first")
        if total_community >= 10:
            award("community_10")
    except Exception as e:
        logger.debug(f"Community badge check skipped (tables may not exist yet): {e}")

    # Archetype set
    bp = supabase.table("user_bias_profiles").select("archetype").eq("user_id", user_id).execute().data or []
    if bp and bp[0].get("archetype"):
        award("archetype_set")

    return newly_awarded

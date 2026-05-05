"""
In-process job scheduler using APScheduler (AsyncIOScheduler).
Jobs run inside the FastAPI process — no separate worker needed.

Free alternative to Celery for low-traffic scheduled tasks.
For high-scale: move to Supabase pg_cron or a Render cron worker.

Add to requirements.txt:  apscheduler>=3.10.0
"""
import logging
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="UTC")


async def _daily_journal_nudge() -> None:
    """
    Runs daily at 19:00 UTC.
    Finds users who have daily notifications enabled and haven't journaled today.
    Sends a reminder email.
    """
    from services.supabase_client import get_supabase
    from services.email_service import send_daily_reminder

    supabase = get_supabase()
    logger.info("[Scheduler] Running daily journal nudge")

    try:
        # Users with daily notifications ON
        profiles = supabase.table("profiles").select("id,display_name,preferences").execute()
        for p in (profiles.data or []):
            prefs = p.get("preferences") or {}
            if not prefs.get("notifications", {}).get("daily", True):
                continue

            user_id = p["id"]
            # Check if they journaled today
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            today_entries = supabase.table("journal_entries").select("id,created_at").eq("user_id", user_id).gte("created_at", today_start).execute()
            if today_entries.data:
                continue  # Already journaled today

            # Get email from auth
            try:
                auth_user = supabase.auth.admin.get_user_by_id(user_id)
                email = getattr(auth_user.user, "email", None) if auth_user else None
            except Exception:
                continue
            if not email:
                continue

            # Compute streak
            all_entries = supabase.table("journal_entries").select("created_at").eq("user_id", user_id).order("created_at", desc=True).limit(30).execute()
            streak = _compute_streak(all_entries.data or [])

            name = p.get("display_name") or email.split("@")[0]
            await send_daily_reminder(email, name, streak)
            logger.info(f"[Scheduler] Daily nudge sent to {email}")

    except Exception as e:
        logger.error(f"[Scheduler] daily_journal_nudge error: {e}")


async def _weekly_digest() -> None:
    """
    Runs every Monday at 08:00 UTC.
    Sends each user a personalized weekly digest email.
    """
    from services.supabase_client import get_supabase
    from services.email_service import send_weekly_digest
    from collections import Counter

    supabase = get_supabase()
    logger.info("[Scheduler] Running weekly digest")

    try:
        profiles = supabase.table("profiles").select("id,display_name,preferences").execute()
        for p in (profiles.data or []):
            prefs = p.get("preferences") or {}
            if not prefs.get("notifications", {}).get("weekly", True):
                continue

            user_id = p["id"]
            week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

            # Collect last 7 days of journal entries
            entries = supabase.table("journal_entries").select("detected_biases,themes,sentiment_score,created_at").eq("user_id", user_id).gte("created_at", week_ago).execute()

            # Build insights
            all_themes: list[str] = []
            all_sentiment: list[float] = []
            entry_count = len(entries.data or [])
            for e in (entries.data or []):
                all_themes.extend(e.get("themes") or [])
                if e.get("sentiment_score") is not None:
                    all_sentiment.append(e["sentiment_score"])

            insights = []
            if entry_count > 0:
                insights.append({"text": f"You wrote {entry_count} journal {'entry' if entry_count == 1 else 'entries'} this week."})
            if all_themes:
                top = [t for t, _ in Counter(all_themes).most_common(2)]
                insights.append({"text": f"Your recurring themes: {', '.join(top)}."})
            if all_sentiment:
                avg = sum(all_sentiment) / len(all_sentiment)
                tone = "positive" if avg > 0.2 else ("negative" if avg < -0.2 else "neutral")
                insights.append({"text": f"Your emotional tone this week was generally {tone}."})

            if not insights:
                continue  # Don't send empty digests

            # Get archetype
            bp = supabase.table("user_bias_profiles").select("archetype").eq("user_id", user_id).execute()
            archetype = bp.data[0].get("archetype") if bp.data else None

            # Get email
            try:
                auth_user = supabase.auth.admin.get_user_by_id(user_id)
                email = getattr(auth_user.user, "email", None) if auth_user else None
            except Exception:
                continue
            if not email:
                continue

            name = p.get("display_name") or email.split("@")[0]
            await send_weekly_digest(email, name, insights, archetype)
            logger.info(f"[Scheduler] Weekly digest sent to {email}")

    except Exception as e:
        logger.error(f"[Scheduler] weekly_digest error: {e}")


def _compute_streak(entries: list[dict]) -> int:
    if not entries:
        return 0
    from datetime import date
    seen: set[date] = set()
    for e in entries:
        try:
            d = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).date()
            seen.add(d)
        except Exception:
            pass
    streak = 0
    cursor = datetime.now(timezone.utc).date()
    while cursor in seen:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def start_scheduler() -> None:
    """Register all jobs and start the scheduler. Call once at app startup."""
    scheduler.add_job(
        _daily_journal_nudge,
        CronTrigger(hour=19, minute=0),
        id="daily_nudge",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.add_job(
        _weekly_digest,
        CronTrigger(day_of_week="mon", hour=8, minute=0),
        id="weekly_digest",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info("[Scheduler] Started — daily nudge @ 19:00 UTC, weekly digest @ Mon 08:00 UTC")

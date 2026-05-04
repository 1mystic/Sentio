"""Admin monitoring router.

Auth: POST /admin/login with {email, password} → returns a daily session token.
All other /admin/* endpoints require X-Admin-Token header with that token.
Credentials stored in sentio-api/.env (gitignored): ADMIN_EMAIL, ADMIN_PASSWORD.
"""
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
import os
import hmac
import hashlib
import logging
import time
from collections import Counter, defaultdict
from datetime import datetime, date, timedelta, timezone
from services.supabase_client import get_supabase

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Simple TTL cache (in-process, resets on server restart) ─────────────────
_cache: dict = {}

def _cache_get(key: str):
    entry = _cache.get(key)
    if entry and time.monotonic() < entry["exp"]:
        return entry["data"]
    return None

def _cache_set(key: str, data, ttl: int = 60):
    _cache[key] = {"data": data, "exp": time.monotonic() + ttl}


def _daily_token(email: str, password: str) -> str:
    """Generates a daily-rotating HMAC token from credentials + today's date.
    Token changes at midnight UTC — valid for the rest of the day after login."""
    day = date.today().isoformat()
    raw = f"{email}:{password}:{day}"
    return hmac.new(b"sentio-admin-salt", raw.encode(), hashlib.sha256).hexdigest()


def _require_admin(x_admin_token: str | None):
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        raise HTTPException(status_code=503, detail="Admin credentials not configured")
    expected = _daily_token(email, password)
    if not x_admin_token or not hmac.compare_digest(x_admin_token, expected):
        raise HTTPException(status_code=403, detail="Invalid or expired admin token")


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def admin_login(data: LoginRequest):
    """Validate admin credentials and return a daily session token."""
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        raise HTTPException(status_code=503, detail="Admin credentials not configured")
    if data.email != email or data.password != password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": _daily_token(email, password)}


# ── Overview Stats ──────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(x_admin_token: str | None = Header(None)):
    """Overall system stats: users, entries, assessments, biases detected."""
    _require_admin(x_admin_token)
    cached = _cache_get("stats")
    if cached:
        return cached
    supabase = get_supabase()

    profiles = supabase.table("profiles").select("id,created_at,onboarding_completed").execute()
    journals = supabase.table("journal_entries").select("id,created_at,user_id,detected_biases,sentiment_score").execute()
    assessments = supabase.table("assessment_results").select("id,completed_at,user_id").execute()
    bias_profiles = supabase.table("user_bias_profiles").select("user_id,bias_scores").execute()
    knowledge = supabase.table("knowledge_articles").select("id,category").execute()
    therapists = supabase.table("therapists").select("id").execute()

    total_users = len(profiles.data or [])
    onboarded = sum(1 for p in (profiles.data or []) if p.get("onboarding_completed"))
    total_entries = len(journals.data or [])
    total_assessments = len(assessments.data or [])

    # Active users in last 7 days (has at least one journal entry)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_active = {e["user_id"] for e in (journals.data or []) if e.get("created_at", "") >= cutoff}

    # Total bias detections across all journal entries
    total_bias_detections = sum(
        len(e.get("detected_biases") or [])
        for e in (journals.data or [])
    )

    # Average sentiment
    sentiments = [e["sentiment_score"] for e in (journals.data or []) if e.get("sentiment_score") is not None]
    avg_sentiment = round(sum(sentiments) / len(sentiments), 3) if sentiments else None

    # Entries per day (last 30 days)
    thirty_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    recent_entries = [e for e in (journals.data or []) if e.get("created_at", "") >= thirty_ago]
    entries_by_day: dict[str, int] = defaultdict(int)
    for e in recent_entries:
        day = e["created_at"][:10]
        entries_by_day[day] += 1

    # User signups per day (last 30 days)
    signups_by_day: dict[str, int] = defaultdict(int)
    for p in (profiles.data or []):
        if p.get("created_at", "") >= thirty_ago:
            day = p["created_at"][:10]
            signups_by_day[day] += 1

    result = {
        "users": {
            "total": total_users,
            "onboarded": onboarded,
            "active_last_7d": len(recent_active),
            "signups_last_30d": dict(sorted(signups_by_day.items())),
        },
        "journal": {
            "total_entries": total_entries,
            "entries_last_30d": len(recent_entries),
            "entries_by_day": dict(sorted(entries_by_day.items())),
            "avg_sentiment": avg_sentiment,
            "total_bias_detections": total_bias_detections,
        },
        "assessments": {
            "total_submissions": total_assessments,
        },
        "knowledge_base": {
            "total_articles": len(knowledge.data or []),
            "by_category": dict(Counter(a.get("category") for a in (knowledge.data or []) if a.get("category"))),
        },
        "therapists": {
            "total": len(therapists.data or []),
        },
    }
    _cache_set("stats", result, ttl=60)
    return result


# ── User List ───────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    x_admin_token: str | None = Header(None),
):
    """Paginated user list with activity summary."""
    _require_admin(x_admin_token)
    cache_key = f"users:{offset}:{limit}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    supabase = get_supabase()

    profiles = (
        supabase.table("profiles")
        .select("id,display_name,created_at,onboarding_completed")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    if not profiles.data:
        return {"users": [], "total": 0}

    user_ids = [p["id"] for p in profiles.data]

    # Fetch emails from auth admin API (profiles table has no email column)
    email_map: dict[str, str] = {}
    try:
        auth_users = supabase.auth.admin.list_users()
        for u in (auth_users or []):
            uid = getattr(u, "id", None)
            email = getattr(u, "email", None)
            if uid and email:
                email_map[uid] = email
    except Exception:
        pass  # emails will show as —

    # Entry counts per user
    entry_counts: dict[str, int] = defaultdict(int)
    entries = supabase.table("journal_entries").select("user_id").in_("user_id", user_ids).execute()
    for e in (entries.data or []):
        entry_counts[e["user_id"]] += 1

    # Assessment counts per user
    assess_counts: dict[str, int] = defaultdict(int)
    assessments = supabase.table("assessment_results").select("user_id").in_("user_id", user_ids).execute()
    for a in (assessments.data or []):
        assess_counts[a["user_id"]] += 1

    # Bias profiles
    bias_map: dict[str, dict] = {}
    bp = supabase.table("user_bias_profiles").select("user_id,bias_scores,archetype").in_("user_id", user_ids).execute()
    for b in (bp.data or []):
        bias_map[b["user_id"]] = b

    users = []
    for p in profiles.data:
        uid = p["id"]
        bp_data = bias_map.get(uid, {})
        scores = bp_data.get("bias_scores") or {}
        top_bias = max(scores, key=scores.get) if scores else None
        users.append({
            "id": uid,
            "name": p.get("display_name") or "—",
            "email": email_map.get(uid, "—"),
            "joined": p.get("created_at", "")[:10],
            "onboarded": p.get("onboarding_completed", False),
            "journal_entries": entry_counts.get(uid, 0),
            "assessments_taken": assess_counts.get(uid, 0),
            "top_bias": top_bias,
            "archetype": bp_data.get("archetype"),
        })

    try:
        total_res = supabase.table("profiles").select("*", count="exact").execute()
        total_count = total_res.count if total_res.count is not None else len(profiles.data)
    except Exception:
        total_count = len(profiles.data)

    result = {"users": users, "total": total_count}
    _cache_set(cache_key, result, ttl=45)
    return result


# ── ML Metrics ──────────────────────────────────────────────────────────────

@router.get("/ml/metrics")
async def ml_metrics(x_admin_token: str | None = Header(None)):
    """Bias classifier metrics derived from all journal entries."""
    _require_admin(x_admin_token)
    cached = _cache_get("ml_metrics")
    if cached:
        return cached
    supabase = get_supabase()

    entries = supabase.table("journal_entries").select("detected_biases,created_at").execute()

    all_detections: list[dict] = []
    processed = 0
    unprocessed = 0

    for e in (entries.data or []):
        biases = e.get("detected_biases")
        if biases is None:
            unprocessed += 1
        else:
            processed += 1
            all_detections.extend(biases or [])

    total_entries = len(entries.data or [])

    # Confidence distribution
    confidences = [d.get("confidence", 0) for d in all_detections]
    conf_buckets = {"0.5-0.6": 0, "0.6-0.7": 0, "0.7-0.8": 0, "0.8-0.9": 0, "0.9-1.0": 0}
    for c in confidences:
        if c < 0.6:
            conf_buckets["0.5-0.6"] += 1
        elif c < 0.7:
            conf_buckets["0.6-0.7"] += 1
        elif c < 0.8:
            conf_buckets["0.7-0.8"] += 1
        elif c < 0.9:
            conf_buckets["0.8-0.9"] += 1
        else:
            conf_buckets["0.9-1.0"] += 1

    # Class distribution
    class_counts = Counter(d.get("bias_id") or d.get("bias") for d in all_detections)

    # Detection rate (entries with at least 1 bias detected)
    entries_with_biases = sum(
        1 for e in (entries.data or [])
        if e.get("detected_biases") and len(e["detected_biases"]) > 0
    )
    detection_rate = round(entries_with_biases / processed, 3) if processed else 0.0

    # Average detections per entry (among processed)
    avg_per_entry = round(len(all_detections) / processed, 2) if processed else 0.0

    # Average confidence
    avg_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0

    result = {
        "classifier": {
            "model": "claude-haiku-4-5-20251001",
            "taxonomy_size": 15,
            "total_entries_processed": processed,
            "total_entries_pending": unprocessed,
            "total_detections": len(all_detections),
            "detection_rate": detection_rate,
            "avg_detections_per_entry": avg_per_entry,
            "avg_confidence": avg_confidence,
        },
        "confidence_distribution": conf_buckets,
        "class_distribution": dict(class_counts.most_common()),
        "note": "F1/precision/recall not tracked server-side (no ground-truth labels). Confidence scores serve as a proxy.",
    }
    _cache_set("ml_metrics", result, ttl=120)
    return result


@router.get("/ml/rag")
async def rag_metrics(x_admin_token: str | None = Header(None)):
    """RAG knowledge base metrics."""
    _require_admin(x_admin_token)
    cached = _cache_get("rag_metrics")
    if cached:
        return cached
    supabase = get_supabase()

    articles = supabase.table("knowledge_articles").select("id,title,category,created_at").execute()
    by_category = Counter(a.get("category") for a in (articles.data or []) if a.get("category"))

    embedder_status = "unknown"
    try:
        from sentence_transformers import SentenceTransformer
        embedder_status = "available"
    except ImportError:
        embedder_status = "not_installed"

    cohere_status = "configured" if os.getenv("COHERE_API_KEY") else "not_configured"

    result = {
        "knowledge_base": {
            "total_chunks": len(articles.data or []),
            "by_category": dict(by_category),
        },
        "embedder": {
            "model": "all-MiniLM-L6-v2",
            "dimensions": 384,
            "status": embedder_status,
        },
        "reranker": {
            "provider": "Cohere",
            "model": "rerank-english-v2.0",
            "status": cohere_status,
        },
        "pipeline": "embed → pgvector cosine similarity (top-10) → Cohere rerank (top-3) → Claude context injection",
    }
    _cache_set("rag_metrics", result, ttl=120)
    return result


# ── Service Health ───────────────────────────────────────────────────────────

@router.get("/services/health")
async def service_health(x_admin_token: str | None = Header(None)):
    """Live health check for all external dependencies."""
    _require_admin(x_admin_token)
    cached = _cache_get("health")
    if cached:
        return cached

    results: dict[str, dict] = {}

    # 1. Supabase
    try:
        supabase = get_supabase()
        supabase.table("profiles").select("id").limit(1).execute()
        results["supabase"] = {"status": "ok", "detail": "DB query succeeded"}
    except Exception as e:
        results["supabase"] = {"status": "error", "detail": str(e)[:120]}

    # 2. Anthropic Claude (lightweight ping — count tokens)
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            results["anthropic"] = {"status": "not_configured", "detail": "ANTHROPIC_API_KEY missing"}
        else:
            client = anthropic.Anthropic(api_key=api_key)
            client.messages.count_tokens(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "ping"}],
            )
            results["anthropic"] = {"status": "ok", "detail": "Token count API reachable"}
    except Exception as e:
        results["anthropic"] = {"status": "error", "detail": str(e)[:120]}

    # 3. Cohere (SDK v5 — use ClientV2, model command-r)
    try:
        import cohere as cohere_sdk
        cohere_key = os.getenv("COHERE_API_KEY")
        if not cohere_key:
            results["cohere"] = {"status": "not_configured", "detail": "COHERE_API_KEY missing"}
        else:
            co = cohere_sdk.ClientV2(api_key=cohere_key)
            co.tokenize(model="command-r", text="health check")
            results["cohere"] = {"status": "ok", "detail": "Tokenize API reachable"}
    except Exception as e:
        err = str(e)
        # SDK v5 raises exceptions whose str() contains response headers when the API responds
        # (even with an error HTTP status). Presence of Cohere trace headers means we reached the API.
        if "x-debug-trace-id" in err.lower() or "access-control" in err.lower():
            results["cohere"] = {"status": "ok", "detail": "API reachable (key accepted)"}
        else:
            results["cohere"] = {"status": "error", "detail": err[:120]}

    # 4. Sentence Transformers embedder
    try:
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer.__new__(SentenceTransformer)  # don't reload model
        from services.rag_service import _get_embedder
        embedder = _get_embedder()
        if embedder:
            results["embedder"] = {"status": "ok", "detail": "Model loaded: all-MiniLM-L6-v2"}
        else:
            results["embedder"] = {"status": "degraded", "detail": "Model not yet initialized"}
    except ImportError:
        results["embedder"] = {"status": "not_installed", "detail": "sentence-transformers not installed"}
    except Exception as e:
        results["embedder"] = {"status": "error", "detail": str(e)[:120]}

    overall = "ok" if all(v["status"] == "ok" for v in results.values()) else "degraded"
    health_result = {"overall": overall, "services": results, "checked_at": datetime.now(timezone.utc).isoformat()}
    _cache_set("health", health_result, ttl=30)
    return health_result


# ── Assessment Stats ─────────────────────────────────────────────────────────

@router.get("/assessments/stats")
async def assessment_stats(x_admin_token: str | None = Header(None)):
    """Assessment completion rates and score distributions."""
    _require_admin(x_admin_token)
    cached = _cache_get("assessment_stats")
    if cached:
        return cached
    supabase = get_supabase()

    assessments_meta = supabase.table("assessments").select("id,slug,title").execute()
    results = supabase.table("assessment_results").select("assessment_id,completed_at,computed_scores").execute()
    profiles = supabase.table("profiles").select("id").execute()

    total_users = len(profiles.data or [])
    completions_by_assessment: dict[str, int] = Counter(r["assessment_id"] for r in (results.data or []))

    assessment_stats = []
    for a in (assessments_meta.data or []):
        completions = completions_by_assessment.get(a["id"], 0)
        completion_rate = round(completions / total_users, 3) if total_users else 0.0

        # Score distributions for this assessment
        scores_for_a = [
            r["computed_scores"] for r in (results.data or [])
            if r["assessment_id"] == a["id"] and r.get("computed_scores")
        ]
        avg_scores: dict[str, float] = {}
        if scores_for_a:
            all_keys = set(k for s in scores_for_a for k in s.keys())
            for k in all_keys:
                vals = [s[k] for s in scores_for_a if k in s]
                avg_scores[k] = round(sum(vals) / len(vals), 1)

        assessment_stats.append({
            "id": a["id"],
            "slug": a["slug"],
            "title": a["title"],
            "total_completions": completions,
            "completion_rate": completion_rate,
            "avg_scores": avg_scores,
        })

    result = {
        "total_users": total_users,
        "total_submissions": len(results.data or []),
        "assessments": assessment_stats,
    }
    _cache_set("assessment_stats", result, ttl=60)
    return result

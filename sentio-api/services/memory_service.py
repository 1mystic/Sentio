"""Three-tier memory for Sentio AI Guide.

Tier 1 — Episodic (memory_episodes): per-session summaries embedded in pgvector.
           One row per conversation_id; updated after every turn.
           Decay λ = 0.05 → half-life ≈ 14 days.

Tier 2 — Semantic (user_facts): nightly APScheduler consolidation of old episodes
           into durable user-level facts.
           Decay λ = 0.005 → half-life ≈ 140 days.

Tier 3 — Working (in-flight): the bias-profile + journal-themes cache already in
           routers/ai.py (_USER_CTX_CACHE) — unchanged.

Retrieval score = cosine_sim(q, m) × exp(−λ × age_days) × importance
Cites: MemGPT (Packer 2023); generative agents memory-stream (Park 2023).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from services.llm_client import has_llm, complete_text
from services.rag_service import _get_embedder
from services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _importance(messages: list[dict]) -> float:
    """Heuristic importance score for an episode.

    Longer sessions and sessions that surface biases are more important.
    Clamped to [0.5, 2.0].
    """
    n_turns = len(messages) // 2  # each turn = user + assistant
    bias_hits = sum(
        1 for m in messages
        if m.get("role") == "assistant" and any(
            kw in m.get("content", "").lower()
            for kw in ("bias", "cognitive", "pattern", "tendency", "confirmation", "catastrophiz")
        )
    )
    return min(2.0, max(0.5, 0.5 + 0.1 * n_turns + 0.3 * bias_hits))


async def _summarise_conversation(messages: list[dict]) -> str | None:
    """Generate a 2–3 sentence episodic memory summary."""
    if not has_llm():
        return None

    recent = messages[-10:]
    transcript = "\n".join(f"{m['role'].upper()}: {m['content'][:300]}" for m in recent)

    try:
        return await complete_text(
            system=(
                "You extract concise episodic memory summaries. "
                "Write 2–3 sentences describing what the user discussed and any "
                "cognitive patterns they expressed. Focus on facts useful for "
                "future conversations. Do not include timestamps or filler."
            ),
            messages=[{"role": "user", "content": f"Summarise this AI Guide conversation for memory storage:\n\n{transcript}"}],
            max_tokens=150,
        )
    except Exception as exc:
        logger.warning(f"[Memory] Episode summarisation failed: {exc}")
        return None


async def _extract_facts(episode_summaries: list[str]) -> list[str]:
    """Distil a batch of episode summaries into 2–4 durable user facts."""
    if not has_llm():
        return []

    joined = "\n\n".join(f"- {s}" for s in episode_summaries)
    try:
        raw = await complete_text(
            system=(
                "You extract durable semantic memory facts about a user from "
                "episodic conversation summaries. "
                "Return ONLY a JSON array of 2–4 short factual strings (each ≤ 25 words). "
                "Each fact must be a third-person statement about the user's cognitive "
                "patterns or recurring topics. No filler. No markdown."
            ),
            messages=[{"role": "user", "content": f"Extract semantic facts from these conversation summaries:\n\n{joined}"}],
            max_tokens=256,
        )
        facts = json.loads(raw.strip())
        if isinstance(facts, list):
            return [str(f) for f in facts if f][:4]
    except Exception as exc:
        logger.warning(f"[Memory] Fact extraction failed: {exc}")
    return []


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

async def save_episode(user_id: str, conversation_id: str, messages: list[dict]) -> None:
    """Upsert an episodic memory entry for this conversation session.

    Called after every turn.  One row per conversation_id — the summary is
    regenerated from the latest message list each time (cheap: 2–3 sentences).
    Safe to call concurrently; the unique index on conversation_id prevents
    duplicate inserts.
    """
    if not messages:
        return

    summary = await _summarise_conversation(messages)
    if not summary:
        return

    embedder = _get_embedder()
    if embedder is None:
        return

    try:
        embedding = await asyncio.get_event_loop().run_in_executor(
            None, lambda: embedder.encode(summary).tolist()
        )
    except Exception as exc:
        logger.warning(f"[Memory] Embedding failed: {exc}")
        return

    importance = _importance(messages)
    supabase = get_supabase()

    try:
        existing = (
            supabase.table("memory_episodes")
            .select("id")
            .eq("conversation_id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
        if existing.data:
            supabase.table("memory_episodes").update(
                {"summary": summary, "embedding": embedding, "importance": importance}
            ).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("memory_episodes").insert(
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "summary": summary,
                    "embedding": embedding,
                    "importance": importance,
                }
            ).execute()
        logger.debug(f"[Memory] Episode saved for conv={conversation_id}")
    except Exception as exc:
        logger.error(f"[Memory] save_episode DB error: {exc}")


async def retrieve_memory(user_id: str, query: str, top_k: int = 3) -> str:
    """Return a formatted memory-context string for system prompt injection.

    Calls the match_memory RPC which applies decay-weighted scoring:
        score = cosine_sim × exp(−λ × age_days) × importance
    Returns "" if no memories exist yet (degrades gracefully).
    """
    embedder = _get_embedder()
    if embedder is None:
        return ""

    try:
        embedding = await asyncio.get_event_loop().run_in_executor(
            None, lambda: embedder.encode(query).tolist()
        )
    except Exception as exc:
        logger.warning(f"[Memory] Query embedding failed: {exc}")
        return ""

    supabase = get_supabase()
    try:
        results = supabase.rpc(
            "match_memory",
            {
                "p_user_id": user_id,
                "query_embedding": embedding,
                "match_count": top_k,
            },
        ).execute()
    except Exception as exc:
        logger.warning(f"[Memory] match_memory RPC failed: {exc}")
        return ""

    if not results.data:
        return ""

    # Bump access_count for retrieved facts (fire-and-forget)
    fact_ids = [r["id"] for r in results.data if r.get("source") == "fact"]
    for fid in fact_ids:
        try:
            supabase.rpc("increment_fact_access", {"p_fact_id": fid}).execute()
        except Exception:
            pass

    parts: list[str] = []
    for r in results.data:
        age_days = r.get("age_days", 0)
        if age_days < 1:
            age_str = "today"
        elif age_days < 30:
            age_str = f"{int(age_days)}d ago"
        else:
            age_str = f"{int(age_days / 30)}mo ago"
        label = "REMEMBERED" if r["source"] == "episode" else "KNOWN PATTERN"
        parts.append(f"[{label} {age_str}]: {r['content']}")

    return "\n".join(parts)


async def consolidate_user_episodes(user_id: str) -> int:
    """Nightly: promote old unconsolidated episodes into semantic user_facts.

    Returns the number of facts created.
    """
    supabase = get_supabase()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    try:
        episodes = (
            supabase.table("memory_episodes")
            .select("id,summary")
            .eq("user_id", user_id)
            .eq("consolidated", False)
            .lt("created_at", cutoff)
            .execute()
        )
    except Exception as exc:
        logger.error(f"[Memory] consolidate fetch error: {exc}")
        return 0

    if not episodes.data or len(episodes.data) < 2:
        return 0

    summaries = [e["summary"] for e in episodes.data]
    episode_ids = [e["id"] for e in episodes.data]

    facts = await _extract_facts(summaries)
    if not facts:
        return 0

    embedder = _get_embedder()
    if embedder is None:
        return 0

    created = 0
    for fact_text in facts:
        try:
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, lambda ft=fact_text: embedder.encode(ft).tolist()
            )
            supabase.table("user_facts").insert(
                {
                    "user_id": user_id,
                    "fact": fact_text,
                    "embedding": embedding,
                    "source_episode_ids": episode_ids,
                }
            ).execute()
            created += 1
        except Exception as exc:
            logger.error(f"[Memory] fact insert error: {exc}")

    # Mark source episodes consolidated regardless of how many facts were created
    try:
        supabase.table("memory_episodes").update({"consolidated": True}).in_(
            "id", episode_ids
        ).execute()
    except Exception as exc:
        logger.error(f"[Memory] consolidate mark error: {exc}")

    logger.info(
        f"[Memory] Consolidated {len(episodes.data)} episodes → "
        f"{created} facts for user={user_id}"
    )
    return created


async def get_user_memory(user_id: str) -> dict:
    """Return a user's readable memory state for the /ai/memory panel."""
    supabase = get_supabase()
    try:
        episodes_res = (
            supabase.table("memory_episodes")
            .select("id,summary,importance,consolidated,created_at")
            .eq("user_id", user_id)
            .eq("consolidated", False)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        facts_res = (
            supabase.table("user_facts")
            .select("id,fact,importance,consolidated_at,access_count")
            .eq("user_id", user_id)
            .order("consolidated_at", desc=True)
            .limit(20)
            .execute()
        )
    except Exception as exc:
        logger.error(f"[Memory] get_user_memory error: {exc}")
        return {"episodes": [], "facts": []}

    now = datetime.now(timezone.utc)

    def age_days(iso: str) -> float:
        try:
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            return (now - dt).total_seconds() / 86400
        except Exception:
            return 0.0

    return {
        "episodes": [
            {
                "id": e["id"],
                "summary": e["summary"],
                "importance": e["importance"],
                "age_days": round(age_days(e["created_at"]), 1),
                "created_at": e["created_at"],
            }
            for e in (episodes_res.data or [])
        ],
        "facts": [
            {
                "id": f["id"],
                "fact": f["fact"],
                "importance": f["importance"],
                "access_count": f["access_count"],
                "consolidated_at": f["consolidated_at"],
            }
            for f in (facts_res.data or [])
        ],
    }


async def delete_memory_item(user_id: str, item_id: str, source: str) -> bool:
    """Delete a single episode or fact.  source must be 'episode' or 'fact'."""
    supabase = get_supabase()
    try:
        if source == "episode":
            result = (
                supabase.table("memory_episodes")
                .delete()
                .eq("id", item_id)
                .eq("user_id", user_id)
                .execute()
            )
        elif source == "fact":
            result = (
                supabase.table("user_facts")
                .delete()
                .eq("id", item_id)
                .eq("user_id", user_id)
                .execute()
            )
        else:
            return False
        return bool(result.data)
    except Exception as exc:
        logger.error(f"[Memory] delete_memory_item error: {exc}")
        return False


async def wipe_user_memory(user_id: str) -> None:
    """GDPR: delete all memory rows for a user."""
    supabase = get_supabase()
    try:
        supabase.table("memory_episodes").delete().eq("user_id", user_id).execute()
        supabase.table("user_facts").delete().eq("user_id", user_id).execute()
        logger.info(f"[Memory] Wiped all memory for user={user_id}")
    except Exception as exc:
        logger.error(f"[Memory] wipe_user_memory error: {exc}")

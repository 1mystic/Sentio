"""RAG retrieval eval: precision@3 and MRR before and after Cohere reranking.

Method (auto-labeling / "leave-one-in"):
  For each query in a curated labeled set, the ground truth is the
  knowledge_articles row(s) whose title matches the expected article name
  (handling chunk suffixes like "Confirmation bias (1/3)").

  BEFORE reranking: take top-3 from pgvector cosine similarity only.
  AFTER  reranking: apply Cohere rerank on top-10, then take top-3.

  Metrics computed per query and averaged:
    Precision@3  — fraction of top-3 results that include a relevant chunk
    MRR          — 1 / rank of first relevant result (0 if not in top-10)

Usage (from sentio-api/):
    python scripts/eval_rag.py
    python scripts/eval_rag.py --no-rerank   # skip Cohere step
    python scripts/eval_rag.py --out results.json

Requires: SUPABASE_URL, SUPABASE_SERVICE_KEY in .env
Optional: COHERE_API_KEY in .env (needed for after-rerank metrics)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

# ── path setup (same pattern as db/seed_knowledge.py) ─────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sentence_transformers import SentenceTransformer
from services.supabase_client import get_supabase

# ──────────────────────────────────────────────────────────────────────────────
# Labeled query set — 52 (query, expected_article_title) pairs
# Expected_article_title must be a substring of the seeded article title so that
# chunk suffixes like "(1/3)" are handled automatically.
# ──────────────────────────────────────────────────────────────────────────────
LABELED_QUERIES: list[tuple[str, str]] = [
    # confirmation_bias
    ("Why do I keep looking for evidence that confirms what I already believe?", "Confirmation bias"),
    ("I dismiss facts that contradict my worldview and only accept supporting ones", "Confirmation bias"),
    # dunning_kruger
    ("New learners often overestimate their competence in a skill they just started", "Dunning-Kruger effect"),
    ("Why do people with little knowledge feel more confident than real experts?", "Dunning-Kruger effect"),
    # anchoring
    ("The first price I saw stuck in my head and distorted all my later comparisons", "Anchoring (cognitive bias)"),
    ("How does the initial number I hear affect my final negotiation outcome?", "Anchoring (cognitive bias)"),
    # availability heuristic
    ("After seeing news of a plane crash I believe flying is far more dangerous than driving", "Availability heuristic"),
    ("I judge how likely events are based on how easily I can recall them", "Availability heuristic"),
    # fundamental attribution error
    ("I blamed my colleague's personality for his mistake but excused my own as circumstantial", "Fundamental attribution error"),
    ("Why do we judge others by character but ourselves by situation?", "Fundamental attribution error"),
    # sunk cost
    ("I keep watching a bad movie because I already spent money on the ticket", "Sunk cost fallacy"),
    ("How to stop investing in failing projects just because of past effort?", "Sunk cost fallacy"),
    # overconfidence
    ("Most people think they are better than average drivers when that is statistically impossible", "Overconfidence effect"),
    ("Why do investors consistently overestimate their ability to beat the market?", "Overconfidence effect"),
    # cognitive dissonance
    ("I believe smoking is harmful but I still smoke — how do I handle this tension?", "Cognitive dissonance"),
    ("Holding two contradictory beliefs at the same time causes mental discomfort", "Cognitive dissonance"),
    # catastrophizing
    ("I made a small mistake and now I am convinced my whole career is ruined", "Catastrophizing"),
    ("I spiral into imagining the absolute worst possible outcome from minor setbacks", "Catastrophizing"),
    # all-or-nothing
    ("I missed one workout so I consider my entire fitness journey ruined", "All-or-nothing thinking"),
    ("Black and white thinking that leaves no room for nuance or middle ground", "All-or-nothing thinking"),
    # overgeneralization
    ("I failed three job interviews so I always fail and no one ever wants to hire me", "Overgeneralization"),
    ("Drawing sweeping conclusions from a single negative event using always and never", "Overgeneralization"),
    # cognitive distortion / CBT
    ("Techniques to identify and challenge automatic negative thoughts in therapy", "Cognitive distortion"),
    ("What are the main distorted thinking patterns addressed in cognitive therapy?", "Cognitive behavioral therapy"),
    # catastrophizing from CBT angle
    ("My therapist says I magnify problems far beyond their actual size", "Catastrophizing"),
    # mindfulness
    ("Paying non-judgmental attention to the present moment to reduce anxiety", "Mindfulness"),
    ("How does mindfulness-based therapy reduce depressive relapse?", "Mindfulness-based cognitive therapy"),
    # emotional reasoning
    ("I feel embarrassed therefore I must have done something objectively wrong", "Emotional reasoning"),
    ("Using emotions as evidence for factual claims about reality", "Emotional reasoning"),
    # halo effect
    ("I assumed the attractive candidate must also be more competent and honest", "Halo effect"),
    ("One positive trait causes us to assume many other positive qualities", "Halo effect"),
    # bandwagon effect
    ("I changed my opinion because everyone else seemed to believe something different", "Bandwagon effect"),
    ("Why do people follow the crowd even when it contradicts their own judgment?", "Bandwagon effect"),
    # hindsight bias
    ("I knew that would happen all along even though I had no idea at the time", "Hindsight bias"),
    ("After learning an outcome we believe we predicted it all along", "Hindsight bias"),
    # status quo bias
    ("Why do people prefer to keep things as they are even when change would improve outcomes?", "Status quo bias"),
    ("I resist changing my routine even though I know it is no longer effective", "Status quo bias"),
    # framing effect
    ("Describing surgery as 90% survival rate vs 10% mortality changes patient choice", "Framing effect (psychology)"),
    ("How the presentation of identical information changes decisions", "Framing effect (psychology)"),
    # recency bias
    ("I weight last month's stock performance far more than the past decade of data", "Recency bias"),
    ("Recent events dominate my judgments even when they are statistically unrepresentative", "Recency bias"),
    # metacognition
    ("Thinking about how you think can improve learning strategies and self-regulation", "Metacognition"),
    ("What is metacognition and why does it matter for academic and professional growth?", "Metacognition"),
    # resilience
    ("How can people recover and grow stronger after trauma and adversity?", "Resilience (psychology)"),
    ("Building psychological resilience after difficult life events and setbacks", "Resilience (psychology)"),
    # emotional intelligence
    ("Understanding and managing my own emotions and recognising them in others", "Emotional intelligence"),
    ("Why emotional intelligence predicts success better than IQ in many contexts", "Emotional intelligence"),
    # personalization
    ("I blame myself for things that are clearly outside my control", "Personalization (psychology)"),
    ("Taking excessive personal responsibility for external events and others' moods", "Personalization (psychology)"),
    # planning fallacy
    ("Why do projects almost always take longer and cost more than we initially estimate?", "Planning fallacy"),
    ("I consistently underestimate how long tasks will take even with past experience", "Planning fallacy"),
]


# ──────────────────────────────────────────────────────────────────────────────
# Retrieval helpers
# ──────────────────────────────────────────────────────────────────────────────

def fetch_article_ids(supabase, article_title: str) -> set[str]:
    """Return the set of article IDs whose title starts with article_title.

    Handles chunk suffixes like "Confirmation bias (1/3)".
    """
    # Fetch all titles matching prefix via Supabase ilike
    pattern = f"{article_title}%"
    res = (
        supabase.table("knowledge_articles")
        .select("id,title")
        .ilike("title", pattern)
        .execute()
    )
    return {r["id"] for r in (res.data or [])}


def retrieve_cosine(supabase, embedding: list[float], match_count: int = 10) -> list[dict]:
    """Top-N results by cosine similarity only (no reranking)."""
    res = supabase.rpc(
        "match_knowledge",
        {
            "query_embedding": embedding,
            "match_threshold": 0.0,   # no threshold for eval — measure full range
            "match_count": match_count,
        },
    ).execute()
    return res.data or []


def retrieve_reranked(
    cohere_client, query: str, cosine_docs: list[dict], top_n: int = 3
) -> list[dict]:
    """Rerank cosine results with Cohere, return top_n."""
    if not cosine_docs or len(cosine_docs) <= top_n:
        return cosine_docs[:top_n]
    try:
        reranked = cohere_client.rerank(
            query=query,
            documents=[d["content"] for d in cosine_docs],
            top_n=top_n,
            model="rerank-english-v2.0",
        )
        return [cosine_docs[r.index] for r in reranked.results]
    except Exception as exc:
        print(f"  [warn] Cohere rerank failed: {exc} — falling back to cosine top-{top_n}")
        return cosine_docs[:top_n]


# ──────────────────────────────────────────────────────────────────────────────
# Metric helpers
# ──────────────────────────────────────────────────────────────────────────────

def precision_at_k(docs: list[dict], relevant_ids: set[str], k: int = 3) -> float:
    """Fraction of top-k retrieved docs that are relevant."""
    top_k = docs[:k]
    hits = sum(1 for d in top_k if d["id"] in relevant_ids)
    return hits / k if k > 0 else 0.0


def reciprocal_rank(docs: list[dict], relevant_ids: set[str]) -> float:
    """1/rank of the first relevant document; 0 if none found."""
    for rank, d in enumerate(docs, start=1):
        if d["id"] in relevant_ids:
            return 1.0 / rank
    return 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Main eval loop
# ──────────────────────────────────────────────────────────────────────────────

def run_eval(no_rerank: bool = False) -> dict:
    print("Loading embedding model (all-MiniLM-L6-v2)…")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    supabase = get_supabase()

    # Check article count
    count_res = supabase.table("knowledge_articles").select("id", count="exact").execute()
    article_count = count_res.count if hasattr(count_res, "count") and count_res.count else len(count_res.data or [])
    print(f"knowledge_articles rows: {article_count}")
    if article_count == 0:
        print("ERROR: knowledge_articles table is empty. Run db/seed_knowledge.py first.")
        sys.exit(1)

    cohere_client = None
    if not no_rerank:
        cohere_key = os.getenv("COHERE_API_KEY")
        if cohere_key:
            import cohere
            cohere_client = cohere.Client(cohere_key)
            print("Cohere client ready — will evaluate before AND after reranking.")
        else:
            print("COHERE_API_KEY not set — evaluating cosine-only (no reranking).")
            no_rerank = True

    # Pre-fetch relevant IDs for each unique article title (cache to avoid N×M queries)
    unique_titles = list({title for _, title in LABELED_QUERIES})
    print(f"\nFetching relevant article IDs for {len(unique_titles)} article titles…")
    relevant_id_cache: dict[str, set[str]] = {}
    for title in unique_titles:
        ids = fetch_article_ids(supabase, title)
        relevant_id_cache[title] = ids
        print(f"  {title!r:55s} → {len(ids)} chunk(s)")

    missing = [t for t, ids in relevant_id_cache.items() if not ids]
    if missing:
        print(f"\n[WARN] {len(missing)} expected article(s) not found in DB:")
        for t in missing:
            print(f"  - {t}")
        print("Queries targeting these articles will score 0. Consider re-seeding.")

    print(f"\nRunning eval on {len(LABELED_QUERIES)} queries…")
    rows: list[dict] = []

    for i, (query, article_title) in enumerate(LABELED_QUERIES):
        relevant_ids = relevant_id_cache.get(article_title, set())
        if not relevant_ids:
            # No relevant chunks in DB — score 0 for both metrics
            rows.append({
                "query": query,
                "article": article_title,
                "cosine_p3": 0.0,
                "cosine_mrr": 0.0,
                "rerank_p3": None,
                "rerank_mrr": None,
                "note": "article_not_seeded",
            })
            continue

        # Embed query
        embedding = embedder.encode(query).tolist()

        # Retrieve (cosine-only, top-10)
        cosine_docs = retrieve_cosine(supabase, embedding, match_count=10)

        cosine_p3 = precision_at_k(cosine_docs, relevant_ids, k=3)
        cosine_mrr = reciprocal_rank(cosine_docs, relevant_ids)

        rerank_p3 = None
        rerank_mrr = None
        if not no_rerank and cohere_client is not None:
            reranked_docs = retrieve_reranked(cohere_client, query, cosine_docs, top_n=3)
            rerank_p3 = precision_at_k(reranked_docs, relevant_ids, k=3)
            rerank_mrr = reciprocal_rank(reranked_docs, relevant_ids)
            time.sleep(0.15)  # Cohere rate-limit buffer

        rows.append({
            "query": query,
            "article": article_title,
            "cosine_p3": cosine_p3,
            "cosine_mrr": cosine_mrr,
            "rerank_p3": rerank_p3,
            "rerank_mrr": rerank_mrr,
            "note": "",
        })

        marker = "✓" if cosine_p3 > 0 else "✗"
        rerank_str = f"  rerank_p3={rerank_p3:.2f}" if rerank_p3 is not None else ""
        print(f"  [{i+1:2d}] {marker} cosine_p3={cosine_p3:.2f} mrr={cosine_mrr:.3f}{rerank_str}  {query[:60]}")

    # Aggregate metrics
    valid = [r for r in rows if r["note"] != "article_not_seeded"]
    n_valid = len(valid)

    mean_cosine_p3  = sum(r["cosine_p3"]  for r in valid) / n_valid if n_valid else 0.0
    mean_cosine_mrr = sum(r["cosine_mrr"] for r in valid) / n_valid if n_valid else 0.0

    rerank_rows = [r for r in valid if r["rerank_p3"] is not None]
    n_rerank = len(rerank_rows)
    mean_rerank_p3  = sum(r["rerank_p3"]  for r in rerank_rows) / n_rerank if n_rerank else None
    mean_rerank_mrr = sum(r["rerank_mrr"] for r in rerank_rows) / n_rerank if n_rerank else None

    results = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "n_queries": len(LABELED_QUERIES),
        "n_scored": n_valid,
        "n_missing_articles": len(LABELED_QUERIES) - n_valid,
        "cosine_precision_at_3": round(mean_cosine_p3, 4),
        "cosine_mrr": round(mean_cosine_mrr, 4),
        "rerank_precision_at_3": round(mean_rerank_p3, 4) if mean_rerank_p3 is not None else None,
        "rerank_mrr": round(mean_rerank_mrr, 4) if mean_rerank_mrr is not None else None,
        "lift_precision_at_3": (
            round(mean_rerank_p3 - mean_cosine_p3, 4)
            if mean_rerank_p3 is not None else None
        ),
        "lift_mrr": (
            round(mean_rerank_mrr - mean_cosine_mrr, 4)
            if mean_rerank_mrr is not None else None
        ),
        "rows": rows,
    }

    # Print summary
    print(f"\n{'='*60}")
    print(f"RAG EVAL RESULTS  ({n_valid}/{len(LABELED_QUERIES)} queries scored)")
    print(f"{'='*60}")
    print(f"  Cosine-only   Precision@3 = {mean_cosine_p3:.4f}   MRR = {mean_cosine_mrr:.4f}")
    if mean_rerank_p3 is not None:
        lift_p3  = mean_rerank_p3 - mean_cosine_p3
        lift_mrr = mean_rerank_mrr - mean_cosine_mrr  # type: ignore[operator]
        print(f"  After rerank  Precision@3 = {mean_rerank_p3:.4f}   MRR = {mean_rerank_mrr:.4f}")
        print(f"  Rerank lift   Precision@3 = {lift_p3:+.4f}   MRR = {lift_mrr:+.4f}")
    else:
        print("  (Cohere reranking not evaluated — set COHERE_API_KEY to enable)")
    print(f"{'='*60}")

    return results


def write_results_json(results: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults written to: {path}")


def update_results_md(results: dict) -> None:
    """Append or update the RAG section in RESULTS.md (repo root)."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    md_path = os.path.join(repo_root, "RESULTS.md")

    p3_cosine = results["cosine_precision_at_3"]
    mrr_cosine = results["cosine_mrr"]
    p3_rerank = results.get("rerank_precision_at_3")
    mrr_rerank = results.get("rerank_mrr")
    lift_p3  = results.get("lift_precision_at_3")
    lift_mrr = results.get("lift_mrr")
    n_q      = results["n_queries"]
    n_sc     = results["n_scored"]
    ts       = results["run_at"]

    rerank_row = (
        f"| After Cohere rerank  | {p3_rerank:.4f}        | {mrr_rerank:.4f} |"
        if p3_rerank is not None else
        "| After Cohere rerank  | N/A (key missing) | N/A  |"
    )
    lift_row = (
        f"| **Rerank lift**      | **{lift_p3:+.4f}**    | **{lift_mrr:+.4f}** |"
        if lift_p3 is not None else ""
    )

    section = f"""
## WS-3 RAG Retrieval Eval

Run: {ts}
Queries: {n_sc}/{n_q} scored (remainder: article not yet seeded)
Method: auto-labeling — query generated per article, ground truth = that article's chunks
Match threshold: 0.0 (eval), 0.65 (production); match_count = 10

| Condition            | Precision@3    | MRR    |
|----------------------|---------------|--------|
| Cosine-only (before) | {p3_cosine:.4f}        | {mrr_cosine:.4f} |
{rerank_row}
{lift_row}

**Interpretation**: Rerank lift shows the value added by Cohere's cross-encoder
reranker over pure vector similarity. Positive lift = reranker improves ranking.
"""

    # Read existing RESULTS.md or create fresh
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Replace the WS-3 RAG section if it exists
        import re
        content = re.sub(
            r"\n## WS-3 RAG Retrieval Eval.*?(?=\n## |\Z)",
            section,
            content,
            flags=re.DOTALL,
        )
        if "## WS-3 RAG Retrieval Eval" not in content:
            content += section
    else:
        content = f"# Sentio — Eval Results\n{section}"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"RESULTS.md updated: {md_path}")


# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sentio RAG retrieval eval")
    parser.add_argument(
        "--no-rerank", action="store_true",
        help="Skip Cohere reranking (cosine-only metrics)",
    )
    parser.add_argument(
        "--out", default="scripts/rag_eval_results.json",
        help="JSON output path (default: scripts/rag_eval_results.json)",
    )
    args = parser.parse_args()

    results = run_eval(no_rerank=args.no_rerank)
    write_results_json(results, args.out)
    update_results_md(results)


if __name__ == "__main__":
    main()

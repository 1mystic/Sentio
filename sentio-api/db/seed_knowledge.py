"""Seed the knowledge_articles table with psychology content for RAG.

Fetches Wikipedia psychology/cognitive-bias articles, chunks them, embeds each
chunk with all-MiniLM-L6-v2 (384-dim), and inserts into Supabase.

Usage (from repo root or sentio-api/):
    python db/seed_knowledge.py           # insert only
    python db/seed_knowledge.py --clear   # wipe table then insert
    python db/seed_knowledge.py --dry-run # fetch+chunk but don't insert
"""
import os
import re
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

import requests
from sentence_transformers import SentenceTransformer
from services.supabase_client import get_supabase

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_WORDS = 400
CHUNK_OVERLAP = 50
WIKI_API = "https://en.wikipedia.org/w/api.php"

# (title, category) pairs — ~45 articles -> ~100-150 chunks after splitting
ARTICLES = [
    # Core cognitive biases
    ("Confirmation bias",                 "cognitive_bias"),
    ("Dunning-Kruger effect",             "cognitive_bias"),
    ("Anchoring (cognitive bias)",        "cognitive_bias"),
    ("Availability heuristic",            "cognitive_bias"),
    ("Fundamental attribution error",     "cognitive_bias"),
    ("Sunk cost fallacy",                 "cognitive_bias"),
    ("Overconfidence effect",             "cognitive_bias"),
    ("Cognitive dissonance",              "cognitive_bias"),
    ("Hindsight bias",                    "cognitive_bias"),
    ("Self-serving bias",                 "cognitive_bias"),
    ("In-group favoritism",               "cognitive_bias"),
    ("Illusory superiority",              "cognitive_bias"),
    ("Planning fallacy",                  "cognitive_bias"),
    ("Gambler's fallacy",                 "cognitive_bias"),
    ("Clustering illusion",               "cognitive_bias"),
    ("Recency bias",                      "cognitive_bias"),
    ("Status quo bias",                   "cognitive_bias"),
    ("Framing effect (psychology)",       "cognitive_bias"),
    ("Bandwagon effect",                  "cognitive_bias"),
    ("Halo effect",                       "cognitive_bias"),
    # Cognitive distortions (CBT)
    ("Cognitive distortion",              "cognitive_distortion"),
    ("Catastrophizing",                   "cognitive_distortion"),
    ("All-or-nothing thinking",           "cognitive_distortion"),
    ("Overgeneralization",                "cognitive_distortion"),
    ("Emotional reasoning",               "cognitive_distortion"),
    ("Personalization (psychology)",      "cognitive_distortion"),
    ("Labeling (psychology)",             "cognitive_distortion"),
    ("Minimisation (psychology)",         "cognitive_distortion"),
    # Therapy & interventions
    ("Cognitive behavioral therapy",      "therapy"),
    ("Metacognitive therapy",             "therapy"),
    ("Rational emotive behavior therapy", "therapy"),
    ("Mindfulness-based cognitive therapy","therapy"),
    ("Acceptance and commitment therapy", "therapy"),
    ("Dialectical behavior therapy",      "therapy"),
    ("Exposure therapy",                  "therapy"),
    # Psychology foundations
    ("Metacognition",                     "psychology"),
    ("Heuristic (psychology)",            "psychology"),
    ("Decision-making",                   "psychology"),
    ("Emotional intelligence",            "psychology"),
    ("Self-awareness",                    "psychology"),
    ("Cognitive psychology",              "psychology"),
    ("Positive psychology",               "psychology"),
    ("Resilience (psychology)",           "psychology"),
    ("Mindfulness",                       "psychology"),
    ("Mental health",                     "psychology"),
]


def fetch_wikipedia(title: str, retries: int = 3) -> tuple[str, str] | None:
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
        "format": "json",
    }
    for attempt in range(retries):
        try:
            r = requests.get(WIKI_API, params=params, timeout=15,
                             headers={"User-Agent": "Sentio/1.0 seed_knowledge.py"})
            if r.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"  [rate-limit] {title}: waiting {wait}s before retry {attempt + 1}/{retries}")
                time.sleep(wait)
                continue
            r.raise_for_status()
            pages = r.json()["query"]["pages"]
            page = next(iter(pages.values()))
            if "extract" not in page or not page["extract"].strip():
                return None
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            return page["extract"], url
        except Exception as exc:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            print(f"  [warn] {title}: {exc}")
            return None
    print(f"  [warn] {title}: exhausted retries")
    return None


def clean(text: str) -> str:
    text = re.sub(r"={2,}[^=]+=={2,}", "", text)   # section headers
    text = re.sub(r"\[\d+\]", "", text)              # citation markers
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk(text: str) -> list[str]:
    words = text.split()
    if len(words) <= CHUNK_WORDS:
        return [text]
    chunks, start = [], 0
    while start < len(words):
        chunks.append(" ".join(words[start : start + CHUNK_WORDS]))
        start += CHUNK_WORDS - CHUNK_OVERLAP
    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clear",   action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    supabase = get_supabase()

    if args.clear:
        print("Clearing knowledge_articles table…")
        # Delete all rows (Supabase requires a filter; neq on primary key selects all)
        supabase.table("knowledge_articles").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000"
        ).execute()
        print("  Cleared.")

    # Load already-inserted titles to avoid duplicates on re-runs
    existing_resp = supabase.table("knowledge_articles").select("title").execute()
    existing_titles: set[str] = set()
    for row in (existing_resp.data or []):
        # Strip chunk suffix like " (2/8)" to get the base title
        base = re.sub(r"\s*\(\d+/\d+\)$", "", row["title"])
        existing_titles.add(base)

    total, failed = 0, []

    for title, category in ARTICLES:
        if title in existing_titles:
            print(f"\n-> {title} [{category}] - already seeded, skipping")
            continue
        print(f"\n-> {title} [{category}]")
        result = fetch_wikipedia(title)
        if result is None:
            failed.append(title)
            continue

        raw, url = result
        text = clean(raw)
        pieces = chunk(text)
        word_count = len(text.split())
        print(f"  {word_count} words -> {len(pieces)} chunk(s)")

        if args.dry_run:
            continue

        embeddings = model.encode(pieces, normalize_embeddings=True).tolist()

        rows = [
            {
                "title": f"{title} ({i+1}/{len(pieces)})" if len(pieces) > 1 else title,
                "content": piece,
                "category": category,
                "source_url": url,
                "source_citation": (
                    f"Wikipedia contributors. \"{title}\". "
                    "Wikipedia, The Free Encyclopedia. "
                    "https://en.wikipedia.org"
                ),
                "embedding": emb,
            }
            for i, (piece, emb) in enumerate(zip(pieces, embeddings))
        ]

        supabase.table("knowledge_articles").insert(rows).execute()
        total += len(rows)
        print(f"  + inserted {len(rows)} row(s)")
        time.sleep(1.5)  # Wikipedia rate-limit buffer

    print(f"\n{'='*50}")
    if args.dry_run:
        print("Dry-run complete. Nothing inserted.")
    else:
        print(f"Done. {total} chunks inserted from {len(ARTICLES) - len(failed)} articles.")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")


if __name__ == "__main__":
    main()

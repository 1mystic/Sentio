"""Cognitive bias classifier eval: per-class precision, recall, F1 + agreement rate.

Runs the production bias_classifier (Claude Haiku) against 30 human-labeled
journal entry snippets, 2 per class across all 15 taxonomy classes.

Cost: ~30 × $0.0002 ≈ $0.006 in Claude API credits.

Usage (from sentio-api/):
    python scripts/eval_bias.py
    python scripts/eval_bias.py --out scripts/bias_eval_results.json

Requires: ANTHROPIC_API_KEY in .env
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

# ── path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from services.bias_classifier import classify_biases

# ──────────────────────────────────────────────────────────────────────────────
# Ground-truth labeled dataset — 30 entries, 2 per class
# Each entry has one primary expected bias.  For attribution_error /
# fundamental_attribution (which are adjacent in the taxonomy) both are listed
# as valid expected labels and either counts as TP.
# ──────────────────────────────────────────────────────────────────────────────
ALL_CLASSES = [
    "confirmation_bias", "attribution_error", "all_or_nothing", "catastrophizing",
    "mind_reading", "overgeneralization", "emotional_reasoning", "should_statements",
    "labeling", "personalization", "availability_bias", "anchoring_bias",
    "dunning_kruger", "sunk_cost_fallacy", "fundamental_attribution",
]

LABELED_ENTRIES: list[dict] = [
    # ── confirmation_bias ─────────────────────────────────────────────────────
    {
        "text": (
            "I only read news sources that already agree with my political views. "
            "When my friend shared an opposing article, I immediately dismissed it "
            "as propaganda without reading it. I know I'm right about this and "
            "every source I trust confirms it."
        ),
        "expected": ["confirmation_bias"],
    },
    {
        "text": (
            "I searched online for studies that supported my dietary choices and "
            "bookmarked fifteen articles. When my doctor showed me a meta-analysis "
            "suggesting otherwise, I said the study was probably funded by industry. "
            "I've already made up my mind — the evidence I've collected is solid."
        ),
        "expected": ["confirmation_bias"],
    },
    # ── attribution_error / fundamental_attribution ───────────────────────────
    {
        "text": (
            "My colleague submitted the report late because she's careless and "
            "disorganised — that's just who she is. When I was late last month it "
            "was because of a system outage and an unrealistic deadline from above. "
            "Completely different situations, obviously."
        ),
        "expected": ["attribution_error", "fundamental_attribution"],
    },
    {
        "text": (
            "The driver who cut me off is clearly an aggressive, selfish person. "
            "When I cut someone off last week I was running late to a genuine "
            "emergency. I had no choice; he chose to be rude."
        ),
        "expected": ["attribution_error", "fundamental_attribution"],
    },
    # ── all_or_nothing ────────────────────────────────────────────────────────
    {
        "text": (
            "I missed one workout this week so my entire fitness journey is ruined. "
            "I'm either fully committed to the gym every single day or I'm a "
            "complete failure at health. There is no point continuing since I "
            "already broke the streak."
        ),
        "expected": ["all_or_nothing"],
    },
    {
        "text": (
            "I got a B+ on the exam instead of an A. I am not a good student. "
            "Either I ace everything perfectly or I'm a complete academic failure. "
            "I don't see the point of studying if I cannot do it right."
        ),
        "expected": ["all_or_nothing"],
    },
    # ── catastrophizing ───────────────────────────────────────────────────────
    {
        "text": (
            "I made a small mistake in my presentation today. Now my boss will "
            "think I'm incompetent, I'll get fired, I won't be able to pay rent, "
            "and I'll end up on the street. This one slip-up is going to completely "
            "destroy my career and my life."
        ),
        "expected": ["catastrophizing"],
    },
    {
        "text": (
            "I got a slightly critical comment on my code review. This means I'm "
            "a terrible developer. I'll never get promoted. Everyone will eventually "
            "realise I'm not good enough and I'll be stuck at this level forever."
        ),
        "expected": ["catastrophizing"],
    },
    # ── mind_reading ──────────────────────────────────────────────────────────
    {
        "text": (
            "I can tell my friend thinks I'm boring — he barely responded to my "
            "last message. My manager is definitely disappointed in me even though "
            "she hasn't said anything negative. I just know what people think about "
            "me without them needing to say it."
        ),
        "expected": ["mind_reading"],
    },
    {
        "text": (
            "Everyone at the party was thinking how awkward I was — I could see it "
            "on their faces even if they said nothing. My date probably thought I "
            "was terrible company. I always know these things; I can read people."
        ),
        "expected": ["mind_reading"],
    },
    # ── overgeneralization ────────────────────────────────────────────────────
    {
        "text": (
            "I applied to five jobs and was rejected from all of them. I always "
            "fail at job applications. No company ever wants to hire me. This "
            "always happens to me, every single time I try."
        ),
        "expected": ["overgeneralization"],
    },
    {
        "text": (
            "My first relationship ended badly. Relationships never work out for "
            "me. Everyone I date eventually leaves. I should never trust anyone "
            "romantically because it always ends in heartbreak."
        ),
        "expected": ["overgeneralization"],
    },
    # ── emotional_reasoning ───────────────────────────────────────────────────
    {
        "text": (
            "I feel like a fraud in this job even though my performance reviews "
            "are excellent. The feeling is so strong that it must be true — I'm "
            "probably fooling everyone and they just haven't figured it out yet. "
            "My feelings don't lie."
        ),
        "expected": ["emotional_reasoning"],
    },
    {
        "text": (
            "I felt terrified during the flight, so flying must genuinely be "
            "extremely dangerous. My gut was screaming danger the entire time. "
            "If it felt that scary, it objectively was that scary — I trust "
            "my emotions more than statistics."
        ),
        "expected": ["emotional_reasoning"],
    },
    # ── should_statements ─────────────────────────────────────────────────────
    {
        "text": (
            "I should be working harder than this. I must be productive every "
            "single hour. I have to respond to every message within minutes. "
            "I shouldn't need breaks or downtime — that's for lazy people. "
            "I must never waste a single moment."
        ),
        "expected": ["should_statements"],
    },
    {
        "text": (
            "People should always be grateful for what they have. My colleagues "
            "must work as hard as I do. They have to maintain the same standards "
            "and everyone should know better than to complain about minor issues."
        ),
        "expected": ["should_statements"],
    },
    # ── labeling ──────────────────────────────────────────────────────────────
    {
        "text": (
            "I forgot to pay a bill on time. I'm such an idiot. I'm completely "
            "irresponsible. My roommate is a slob because he left one dish in the "
            "sink. My colleague is a narcissist because he talked a lot in one meeting."
        ),
        "expected": ["labeling"],
    },
    {
        "text": (
            "I made an error in the report. I'm not someone who made a mistake — "
            "I am fundamentally a failure as a professional. My manager is a control "
            "freak. The new hire is a complete moron."
        ),
        "expected": ["labeling"],
    },
    # ── personalization ───────────────────────────────────────────────────────
    {
        "text": (
            "My friend seems sad today and I feel terrible because it must be my "
            "fault somehow. Maybe I said something wrong last week. I'm probably "
            "responsible for her mood even though she told me it was about her "
            "work situation."
        ),
        "expected": ["personalization"],
    },
    {
        "text": (
            "Our team project failed and even though I was one of six people, "
            "I keep thinking I should have done more, that it's fundamentally "
            "my fault. The team dynamic suffered because I wasn't good enough "
            "to fix everything."
        ),
        "expected": ["personalization"],
    },
    # ── availability_bias ─────────────────────────────────────────────────────
    {
        "text": (
            "Ever since I saw news coverage of a shark attack, I've been terrified "
            "of swimming in the ocean. I now think attacks happen all the time. "
            "I judge how likely something is based on how easily I can recall it "
            "happening, not on actual statistics."
        ),
        "expected": ["availability_bias"],
    },
    {
        "text": (
            "A plane crash was on the news last week and now I'm refusing to fly. "
            "Statistically cars are far more dangerous but I feel flying is "
            "incredibly risky because the crash footage is so vivid in my memory."
        ),
        "expected": ["availability_bias"],
    },
    # ── anchoring_bias ────────────────────────────────────────────────────────
    {
        "text": (
            "The first salary figure the recruiter mentioned was 60k. Even though "
            "I know my market rate is higher, all my negotiation thinking revolves "
            "around that initial number. I can't get it out of my head."
        ),
        "expected": ["anchoring_bias"],
    },
    {
        "text": (
            "The dealer showed me a 50,000 rupee phone first. When they showed me "
            "the 35,000 version next, it felt like a bargain even though it's still "
            "very expensive by any normal standard. I kept comparing everything to "
            "that first price."
        ),
        "expected": ["anchoring_bias"],
    },
    # ── dunning_kruger ────────────────────────────────────────────────────────
    {
        "text": (
            "I took a beginner Python course last month and I'm now confident I "
            "could build any application. I don't need to study more — I understand "
            "programming fundamentally. Other developers just overcomplicate things."
        ),
        "expected": ["dunning_kruger"],
    },
    {
        "text": (
            "After reading three investment books I'm certain I can consistently "
            "beat professional fund managers. I've understood something they haven't. "
            "My first two successful trades prove my superior market intuition."
        ),
        "expected": ["dunning_kruger"],
    },
    # ── sunk_cost_fallacy ─────────────────────────────────────────────────────
    {
        "text": (
            "I've been in this relationship for five years and even though we make "
            "each other unhappy, I can't leave because of all the time I've already "
            "invested. The thought of those five years being 'wasted' keeps me here."
        ),
        "expected": ["sunk_cost_fallacy"],
    },
    {
        "text": (
            "I spent 2,000 rupees on concert tickets but I'm sick with a fever. "
            "I'm going anyway because I can't waste the money. I know I should "
            "rest, but since I already paid I have no choice."
        ),
        "expected": ["sunk_cost_fallacy"],
    },
    # ── fundamental_attribution ───────────────────────────────────────────────
    # (distinct from attribution_error entries above — focuses on underweighting
    #  situational factors when judging others, without the self-serving contrast)
    {
        "text": (
            "The cashier was rude to me so she must just be a rude, unfriendly "
            "person by nature. I never once considered that she might be having "
            "a terrible day or dealing with a personal crisis at home."
        ),
        "expected": ["fundamental_attribution"],
    },
    {
        "text": (
            "My student keeps submitting work late — he's clearly irresponsible "
            "and doesn't care about learning. I haven't asked whether he's "
            "working two jobs to pay tuition or dealing with a family emergency."
        ),
        "expected": ["fundamental_attribution"],
    },
]

assert len(LABELED_ENTRIES) == 30, f"Expected 30 entries, got {len(LABELED_ENTRIES)}"


# ──────────────────────────────────────────────────────────────────────────────
# Metrics
# ──────────────────────────────────────────────────────────────────────────────

def compute_metrics(all_results: list[dict]) -> dict:
    """
    For each class:
      TP: expected bias detected (confidence >= 0.5)
      FN: expected bias NOT detected
      FP: bias detected that is NOT in expected list

    Returns per-class precision/recall/F1 and macro averages.
    """
    # Per-class counters
    tp: dict[str, int] = defaultdict(int)
    fp: dict[str, int] = defaultdict(int)
    fn: dict[str, int] = defaultdict(int)

    agreement_count = 0  # entries where >= 1 expected bias was detected

    for row in all_results:
        expected_set = set(row["expected"])
        predicted_set = set(row["predicted"])

        # TPs and FNs from expected
        any_hit = False
        for cls in expected_set:
            if cls in predicted_set:
                tp[cls] += 1
                any_hit = True
            else:
                fn[cls] += 1

        # FPs from predicted
        for cls in predicted_set:
            if cls not in expected_set:
                fp[cls] += 1

        if any_hit:
            agreement_count += 1

    agreement_rate = agreement_count / len(all_results) if all_results else 0.0

    # Per-class metrics
    per_class: dict[str, dict] = {}
    for cls in ALL_CLASSES:
        _tp, _fp, _fn = tp[cls], fp[cls], fn[cls]
        precision = _tp / (_tp + _fp) if (_tp + _fp) > 0 else 0.0
        recall    = _tp / (_tp + _fn) if (_tp + _fn) > 0 else 0.0
        f1        = (2 * precision * recall / (precision + recall)
                     if (precision + recall) > 0 else 0.0)
        per_class[cls] = {
            "tp": _tp, "fp": _fp, "fn": _fn,
            "precision": round(precision, 4),
            "recall":    round(recall,    4),
            "f1":        round(f1,        4),
        }

    # Macro averages (only over classes that appear in the ground truth)
    scored_classes = [cls for cls in ALL_CLASSES if (tp[cls] + fn[cls]) > 0]
    macro_precision = sum(per_class[c]["precision"] for c in scored_classes) / len(scored_classes)
    macro_recall    = sum(per_class[c]["recall"]    for c in scored_classes) / len(scored_classes)
    macro_f1        = sum(per_class[c]["f1"]        for c in scored_classes) / len(scored_classes)

    return {
        "agreement_rate": round(agreement_rate, 4),
        "macro_precision": round(macro_precision, 4),
        "macro_recall":    round(macro_recall,    4),
        "macro_f1":        round(macro_f1,        4),
        "per_class": per_class,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

async def run_eval_async() -> tuple[list[dict], dict]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    print(f"Running bias classifier eval on {len(LABELED_ENTRIES)} entries…")
    print("(Each entry calls Claude Haiku — ~$0.006 total)\n")

    all_results: list[dict] = []
    for i, entry in enumerate(LABELED_ENTRIES):
        expected = entry["expected"]
        text = entry["text"]

        try:
            biases = await classify_biases(text)
        except Exception as exc:
            print(f"  [{i+1:2d}] ERROR: {exc}")
            biases = []

        predicted = [b["bias_id"] for b in biases]

        # Determine hit: any expected bias detected?
        hit = any(e in predicted for e in expected)
        marker = "✓" if hit else "✗"

        primary_expected = expected[0]
        print(
            f"  [{i+1:2d}] {marker} expected={primary_expected:25s}  "
            f"predicted={predicted}"
        )

        all_results.append({
            "expected": expected,
            "predicted": predicted,
            "text_preview": text[:80],
            "raw_biases": biases,
        })

    metrics = compute_metrics(all_results)
    return all_results, metrics


def print_summary(metrics: dict) -> None:
    print(f"\n{'='*70}")
    print("BIAS CLASSIFIER EVAL RESULTS")
    print(f"{'='*70}")
    print(f"  Agreement rate (≥1 expected bias detected): {metrics['agreement_rate']:.4f}")
    print(f"  Macro precision: {metrics['macro_precision']:.4f}")
    print(f"  Macro recall:    {metrics['macro_recall']:.4f}")
    print(f"  Macro F1:        {metrics['macro_f1']:.4f}")
    print(f"\n  Per-class breakdown:")
    print(f"  {'Class':30s} {'Prec':6s} {'Rec':6s} {'F1':6s}  TP  FP  FN")
    print(f"  {'-'*65}")
    for cls, m in metrics["per_class"].items():
        print(
            f"  {cls:30s} {m['precision']:6.3f} {m['recall']:6.3f} {m['f1']:6.3f}"
            f"  {m['tp']:2d}  {m['fp']:2d}  {m['fn']:2d}"
        )
    print(f"{'='*70}")


def update_results_md(metrics: dict, n_entries: int) -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    md_path = os.path.join(repo_root, "RESULTS.md")

    ts = datetime.now(timezone.utc).isoformat()
    pc = metrics["per_class"]

    per_class_rows = "\n".join(
        f"| {cls:30s} | {pc[cls]['precision']:.3f}     | {pc[cls]['recall']:.3f}  | {pc[cls]['f1']:.3f} | {pc[cls]['tp']} / {pc[cls]['tp']+pc[cls]['fn']} |"
        for cls in ALL_CLASSES
    )

    section = f"""
## WS-3 Bias Classifier Eval

Run: {ts}
Entries: {n_entries} (2 per class × 15 classes)
Classifier: Claude Haiku via API (services/bias_classifier.py)
Metric: human-agreement (ground truth = author-labeled expected biases)

| Metric           | Value  |
|------------------|--------|
| Agreement rate   | {metrics['agreement_rate']:.4f} |
| Macro precision  | {metrics['macro_precision']:.4f} |
| Macro recall     | {metrics['macro_recall']:.4f} |
| Macro F1         | {metrics['macro_f1']:.4f} |

### Per-class breakdown

| Class                          | Precision | Recall | F1    | TP/Support |
|-------------------------------|-----------|--------|-------|------------|
{per_class_rows}
"""

    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        import re
        content = re.sub(
            r"\n## WS-3 Bias Classifier Eval.*?(?=\n## |\Z)",
            section,
            content,
            flags=re.DOTALL,
        )
        if "## WS-3 Bias Classifier Eval" not in content:
            content += section
    else:
        content = f"# Sentio — Eval Results\n{section}"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"RESULTS.md updated: {md_path}")


def main():
    parser = argparse.ArgumentParser(description="Sentio bias classifier eval")
    parser.add_argument(
        "--out", default="scripts/bias_eval_results.json",
        help="JSON output path (default: scripts/bias_eval_results.json)",
    )
    args = parser.parse_args()

    all_results, metrics = asyncio.run(run_eval_async())

    print_summary(metrics)

    # Write JSON
    output = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "n_entries": len(LABELED_ENTRIES),
        "metrics": metrics,
        "entries": all_results,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults written to: {args.out}")

    update_results_md(metrics, len(LABELED_ENTRIES))


if __name__ == "__main__":
    main()

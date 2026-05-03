"""
Generate synthetic training data for the BiasClassifier using Claude with prompt caching.

Produces 50 journal-entry examples per cognitive bias (15 biases = 750 total).
Each example: { text, bias_labels, explanation, context }

Usage:
    cd sentio-ml
    python data/generate_training_data.py
    python data/generate_training_data.py --bias confirmation_bias --n 10 --dry-run

Output: data/synthetic/bias_training_v1.jsonl
"""
import os
import re
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / "sentio-api" / ".env")

import anthropic

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"
OUTPUT_PATH = Path(__file__).parent / "synthetic" / "bias_training_v1.jsonl"

BIAS_LABELS = [
    "confirmation_bias",
    "attribution_error",
    "all_or_nothing",
    "catastrophizing",
    "mind_reading",
    "overgeneralization",
    "emotional_reasoning",
    "should_statements",
    "labeling",
    "personalization",
    "availability_bias",
    "anchoring_bias",
    "dunning_kruger",
    "sunk_cost_fallacy",
    "fundamental_attribution",
]

BIAS_DESCRIPTIONS = {
    "confirmation_bias": "Seeking or interpreting information that confirms pre-existing beliefs while ignoring contradictory evidence.",
    "attribution_error": "Attributing others' behavior to character flaws while attributing one's own to circumstances.",
    "all_or_nothing": "Seeing situations in black-and-white terms with no middle ground.",
    "catastrophizing": "Assuming the worst possible outcome will occur from a situation.",
    "mind_reading": "Assuming you know what others are thinking without evidence.",
    "overgeneralization": "Drawing broad conclusions from a single event.",
    "emotional_reasoning": "Treating feelings as facts ('I feel stupid, therefore I am stupid').",
    "should_statements": "Rigid rules about how oneself or others must behave.",
    "labeling": "Reducing oneself or others to a single negative trait.",
    "personalization": "Taking excessive personal responsibility for external events.",
    "availability_bias": "Overweighting recent or easily recalled events when making judgments.",
    "anchoring_bias": "Over-relying on the first piece of information encountered.",
    "dunning_kruger": "Overestimating one's competence in areas where one has limited knowledge.",
    "sunk_cost_fallacy": "Continuing a course of action because of past investment rather than future value.",
    "fundamental_attribution": "Underweighting situational factors when judging others' behavior.",
}

# Cached system prompt — sent once, billed once thanks to prompt caching
SYSTEM_PROMPT = """You are a clinical psychologist and cognitive behavioral therapist with expertise in cognitive biases and distortions. You generate realistic, psychologically accurate journal entry examples for training a cognitive bias detection model.

Guidelines for generated examples:
- Write in first-person journal style (casual, reflective, personal)
- Length: 80-200 words per entry
- Each entry should contain ONE primary bias, expressed naturally (not stated explicitly)
- Entries can touch on: work, relationships, decisions, emotions, self-reflection
- Language should feel authentic — not overly literary or clinical
- Vary the demographic/context: different life situations, ages, professions
- The bias should be embedded in the reasoning, not just described

Return a JSON array. Each object has:
  - "text": the journal entry
  - "primary_bias": the bias label
  - "co_occurring": list of any secondary biases present (can be empty)
  - "explanation": one sentence explaining WHERE the bias appears in the text
  - "context": one of ["work", "relationships", "decisions", "self", "social"]
"""


def generate_examples_for_bias(
    client: anthropic.Anthropic,
    bias: str,
    n: int = 50,
) -> list[dict]:
    description = BIAS_DESCRIPTIONS[bias]
    user_prompt = f"""Generate {n} diverse journal entry examples exhibiting **{bias}** ({description}).

Return ONLY a JSON array (no markdown, no explanation) with exactly {n} objects in this format:
[
  {{
    "text": "...",
    "primary_bias": "{bias}",
    "co_occurring": [],
    "explanation": "...",
    "context": "work|relationships|decisions|self|social"
  }},
  ...
]"""

    log.info(f"Generating {n} examples for {bias}…")
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},  # cache the 400-token system prompt
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    try:
        examples = json.loads(raw)
        log.info(f"  ✓ {len(examples)} examples (cached={response.usage.cache_read_input_tokens})")
        return examples
    except json.JSONDecodeError as exc:
        log.error(f"  JSON parse failed for {bias}: {exc}")
        log.debug(f"  Raw response: {raw[:500]}")
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bias",    help="Generate for one specific bias only")
    parser.add_argument("--n",       type=int, default=50, help="Examples per bias (default 50)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)

    targets = [args.bias] if args.bias else BIAS_LABELS
    invalid = [b for b in targets if b not in BIAS_LABELS]
    if invalid:
        sys.exit(f"Unknown bias labels: {invalid}\nValid: {BIAS_LABELS}")

    if args.dry_run:
        log.info(f"Dry-run: would generate {len(targets) * args.n} examples for {targets}")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Append mode so re-runs for individual biases don't overwrite prior work
    mode = "a" if args.bias else "w"
    total = 0

    with open(OUTPUT_PATH, mode, encoding="utf-8") as f:
        for bias in targets:
            examples = generate_examples_for_bias(client, bias, args.n)
            for ex in examples:
                ex["primary_bias"] = bias  # enforce correct label
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
            total += len(examples)
            time.sleep(1)  # avoid rate limiting

    log.info(f"\nDone. {total} examples written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

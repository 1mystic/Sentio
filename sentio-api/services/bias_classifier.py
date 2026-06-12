"""Cognitive bias classifier using Claude Haiku with prompt caching.

Replaces the HuggingFace Space approach — no training, no infrastructure.
Uses claude-haiku-4-5-20251001 (~$0.0002 per journal entry at typical lengths).
The static bias taxonomy is cached with cache_control: ephemeral.
"""
import json
import os
import logging
from services.llm_client import has_llm, complete_text

logger = logging.getLogger(__name__)

_BIAS_TAXONOMY = """COGNITIVE BIAS TAXONOMY (15 classes):

1. confirmation_bias — Seeking or interpreting information that confirms pre-existing beliefs while ignoring contradictory evidence.
2. attribution_error — Attributing others' behavior to character flaws while attributing one's own to circumstances (Fundamental Attribution Error variant).
3. all_or_nothing — Seeing situations in black-and-white terms with no middle ground.
4. catastrophizing — Assuming the worst possible outcome will occur from a situation.
5. mind_reading — Assuming you know what others are thinking without evidence.
6. overgeneralization — Drawing broad conclusions from a single event (uses "always", "never", "everyone", "no one").
7. emotional_reasoning — Treating feelings as facts ("I feel stupid, therefore I am stupid").
8. should_statements — Rigid rules about how oneself or others must behave ("I should", "they must", "I have to").
9. labeling — Reducing oneself or others to a single negative trait ("I'm a failure", "he's an idiot").
10. personalization — Taking excessive personal responsibility for external events.
11. availability_bias — Overweighting recent or easily recalled events when making judgments.
12. anchoring_bias — Over-relying on the first piece of information encountered.
13. dunning_kruger — Overestimating one's competence in areas where one has limited knowledge.
14. sunk_cost_fallacy — Continuing a course of action because of past investment rather than future value.
15. fundamental_attribution — Underweighting situational factors when judging others' behavior."""

_SYSTEM_PROMPT = f"""You are a cognitive bias detection system. Analyze journal entries and identify cognitive biases present in the text.

{_BIAS_TAXONOMY}

Rules:
- Only flag biases that are clearly evidenced in the text
- Do not over-diagnose — most entries will have 0-3 biases
- Confidence must be 0.5-1.0 (never flag below 0.5)
- span: a short direct quote (≤10 words) from the text that most clearly shows the bias; null if none
- Return ONLY valid JSON, no commentary"""

_RESPONSE_FORMAT = """Return a JSON array. Each element:
{"bias_id": "<snake_case_id>", "bias": "<snake_case_id>", "confidence": <0.5–1.0>, "span": "<quote or null>"}

If no biases are detected, return: []

Example:
[
  {"bias_id": "confirmation_bias", "bias": "confirmation_bias", "confidence": 0.82, "span": "I knew this would happen"},
  {"bias_id": "catastrophizing", "bias": "catastrophizing", "confidence": 0.71, "span": "everything is ruined now"}
]"""


async def classify_biases(text: str) -> list[dict]:
    """Classify cognitive biases in a journal entry using Claude Haiku.

    Returns a list of dicts:
        [{"bias_id": "...", "bias": "...", "confidence": 0.87, "span": "..."}]
    """
    if not has_llm():
        logger.warning("No LLM API key configured — skipping bias classification")
        return []

    try:
        raw = await complete_text(
            system=_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Analyze this journal entry for cognitive biases:\n\n<entry>\n{text[:3000]}\n</entry>\n\n{_RESPONSE_FORMAT}",
            }],
            max_tokens=512,
        )
        logger.info("Bias classifier completed")
        raw = raw.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        biases = json.loads(raw)
        if not isinstance(biases, list):
            return []

        # Normalise and validate each entry
        valid = []
        known_ids = {
            "confirmation_bias", "attribution_error", "all_or_nothing",
            "catastrophizing", "mind_reading", "overgeneralization",
            "emotional_reasoning", "should_statements", "labeling",
            "personalization", "availability_bias", "anchoring_bias",
            "dunning_kruger", "sunk_cost_fallacy", "fundamental_attribution",
        }
        for b in biases:
            bias_id = b.get("bias_id") or b.get("bias", "")
            conf = float(b.get("confidence", 0))
            if bias_id in known_ids and conf >= 0.5:
                valid.append({
                    "bias_id": bias_id,
                    "bias": bias_id,
                    "confidence": round(conf, 2),
                    "span": b.get("span"),
                })
        return valid

    except json.JSONDecodeError as e:
        logger.error(f"Bias classifier JSON parse error: {e}")
        return []
    except Exception as e:
        logger.error(f"Bias classifier error: {e}")
        return []

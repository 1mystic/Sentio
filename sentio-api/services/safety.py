"""Content safety checking: crisis detection and clinical overreach prevention."""
import re
from dataclasses import dataclass
from typing import Literal

CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "self-harm", "self harm", "hurt myself", "cutting myself",
    "no reason to live", "better off dead", "overdose", "take my life",
    "end it all", "don't want to be here", "can't go on",
    # Keep legacy variants from original file
    "don't want to live", "dont want to live", "better off without me",
    "not worth living",
]

# Patterns that indicate clinical overreach in AI output
CLINICAL_OVERREACH_PATTERNS = [
    r'\bdiagnos\w*\b',
    r'\bdisorder\b',
    r'\billness\b',
    r'\bmedication\b',
    r'\bprescri\w*\b',
    r'\btherapist says\b',
    r'\byou have\s+\w+\s+(disorder|condition|syndrome)\b',
]

CRISIS_RESPONSE = (
    "It sounds like you may be going through something really difficult. "
    "Please reach out for support:\n\n"
    "**iCall** (TISS): 9152987821\n"
    "**Vandrevala Foundation**: 1860-2662-345\n"
    "**iCall Online**: icallhelpline.org\n\n"
    "You don't have to face this alone. Sentio is an educational tool — "
    "for crisis support, please speak with a trained counsellor."
)


@dataclass
class SafetyResult:
    action: Literal["PROCEED", "REDIRECT"]
    message: str | None = None
    block_ai_response: bool = False


class SafetyChecker:
    """Lightweight content-safety layer for Sentio.

    Input check  — runs before any user text reaches the AI.
    Output check — runs on each streamed chunk before sending to the client.
    """

    def check_input(self, text: str) -> SafetyResult:
        """Return REDIRECT (with crisis resources) if crisis signals detected,
        otherwise PROCEED."""
        lower = text.lower()
        if any(kw in lower for kw in CRISIS_KEYWORDS):
            return SafetyResult(
                action="REDIRECT",
                message=CRISIS_RESPONSE,
                block_ai_response=True,
            )
        return SafetyResult(action="PROCEED")

    def check_output(self, text: str) -> bool:
        """Return True if the output chunk is safe to forward to the client.

        Blocks chunks that contain clinical overreach language.
        """
        for pattern in CLINICAL_OVERREACH_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True


# Module-level singleton — import this everywhere
safety = SafetyChecker()

from dataclasses import dataclass
from typing import Literal

CRISIS_KEYWORDS = [
    "suicide",
    "suicidal",
    "kill myself",
    "end my life",
    "don't want to live",
    "dont want to live",
    "self-harm",
    "self harm",
    "hurt myself",
    "cutting myself",
    "overdose",
    "want to die",
    "better off without me",
    "no reason to live",
    "not worth living",
    "end it all",
]

CRISIS_RESOURCES = (
    "If you're in crisis, please reach out immediately:\n"
    "  iCall (India): 9152987821\n"
    "  Vandrevala Foundation: 1860-2662-345\n"
    "  iCall chat: icallhelpline.org\n"
    "These services are free, confidential, and available 24/7."
)

# Phrases that indicate the AI response is overstepping into clinical territory
_BLOCKED_OUTPUT_PHRASES = [
    "you have",
    "you suffer from",
    "you are diagnosed",
    "take medication",
    "prescribe",
    "clinical diagnosis",
    "you need therapy",
    "you should see a psychiatrist",
]


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
                message=CRISIS_RESOURCES,
                block_ai_response=True,
            )
        return SafetyResult(action="PROCEED")

    def check_output(self, text: str) -> bool:
        """Return True if the output chunk is safe to forward to the client.

        Blocks chunks that contain clinical overreach language.
        """
        lower = text.lower()
        return not any(phrase in lower for phrase in _BLOCKED_OUTPUT_PHRASES)


# Module-level singleton — import this everywhere
safety = SafetyChecker()

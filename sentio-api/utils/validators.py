"""Input validation utilities."""
import re
from typing import Optional

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "self-harm", "self harm", "hurt myself", "cutting myself",
    "no reason to live", "better off dead", "overdose",
]


def contains_crisis_signal(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in CRISIS_KEYWORDS)


def sanitize_text(text: str) -> str:
    """Remove null bytes and strip excess whitespace."""
    return re.sub(r'\s+', ' ', text.replace('\x00', '')).strip()


def validate_uuid(value: str) -> bool:
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return bool(re.match(pattern, value.lower()))


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return max(min_val, min(max_val, value))


def is_valid_mood(mood: Optional[str]) -> bool:
    VALID_MOODS = {"😊", "😐", "😔", "😤", "😴", "happy", "neutral", "sad", "angry", "tired"}
    return mood is None or mood in VALID_MOODS

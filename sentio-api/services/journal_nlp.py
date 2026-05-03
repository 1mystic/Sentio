"""Journal NLP pipeline: sentiment, themes, and emotion analysis.

Calls the HuggingFace Space endpoint if available.
Falls back to a lightweight local fallback using keyword rules.
"""
import httpx
import os
import logging

logger = logging.getLogger(__name__)

# Simple sentiment keywords for fallback
_POSITIVE_WORDS = {"happy", "great", "good", "excited", "grateful", "proud", "confident", "motivated", "calm", "peaceful"}
_NEGATIVE_WORDS = {"sad", "angry", "frustrated", "anxious", "worried", "stressed", "overwhelmed", "confused", "hurt", "disappointed"}


def _keyword_sentiment(text: str) -> float:
    words = set(text.lower().split())
    pos = len(words & _POSITIVE_WORDS)
    neg = len(words & _NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total


def _extract_themes_locally(text: str) -> list[str]:
    """Simple keyword-based theme extraction as fallback."""
    THEME_KEYWORDS = {
        "work": "work-stress", "project": "work-stress", "deadline": "work-stress",
        "team": "teamwork", "colleague": "teamwork", "meeting": "communication",
        "decision": "decision-making", "choice": "decision-making",
        "family": "relationships", "friend": "relationships", "relationship": "relationships",
        "money": "finances", "budget": "finances",
        "health": "health", "exercise": "health",
        "learn": "learning", "study": "learning",
        "goal": "goals", "achieve": "goals",
    }
    found_themes = set()
    lower_text = text.lower()
    for keyword, theme in THEME_KEYWORDS.items():
        if keyword in lower_text:
            found_themes.add(theme)
    return list(found_themes)[:5]


async def analyze_journal(text: str) -> dict:
    """Analyze a journal entry for sentiment, themes, and emotions.

    Tries the configured HF Space endpoint first.
    Falls back to local keyword analysis if unavailable.

    Returns a dict with keys:
        themes          — list of detected theme strings
        sentiment_score — float in [-1.0, 1.0]
        emotions        — list of {label, score} dicts
        word_count      — int
    """
    url = os.getenv("JOURNAL_NLP_URL")

    if url:
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(
                    f"{url}/analyze",
                    json={"text": text[:1000]},  # truncate to avoid timeouts
                    headers={"Authorization": f"Bearer {os.getenv('HF_API_TOKEN', '')}"},
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "themes": data.get("themes", []),
                    "sentiment_score": float(data.get("sentiment_score", 0.0)),
                    "emotions": data.get("emotions", []),
                    "word_count": len(text.split()),
                }
        except httpx.TimeoutException:
            logger.warning("Journal NLP endpoint timed out — using local fallback")
        except Exception as e:
            logger.warning(f"Journal NLP endpoint error: {e} — using local fallback")

    # Local fallback
    sentiment = _keyword_sentiment(text)
    themes = _extract_themes_locally(text)
    word_count = len(text.split())

    # Simple emotion heuristic
    emotions = []
    lower = text.lower()
    if any(w in lower for w in ("frustrated", "angry", "annoyed")):
        emotions.append({"label": "anger", "score": 0.7})
    elif any(w in lower for w in ("sad", "upset", "hurt")):
        emotions.append({"label": "sadness", "score": 0.7})
    elif any(w in lower for w in ("happy", "excited", "grateful")):
        emotions.append({"label": "joy", "score": 0.7})
    elif any(w in lower for w in ("worried", "anxious", "nervous")):
        emotions.append({"label": "fear", "score": 0.6})
    else:
        emotions.append({"label": "neutral", "score": 0.8})

    return {
        "themes": themes,
        "sentiment_score": round(sentiment, 3),
        "emotions": emotions,
        "word_count": word_count,
    }

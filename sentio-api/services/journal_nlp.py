import httpx
import os
import logging

logger = logging.getLogger(__name__)

_EMPTY_RESULT = {"emotions": [], "themes": [], "sentiment_score": 0.0}


async def analyze_journal(text: str) -> dict:
    """Call the HuggingFace Space journal NLP service.

    Returns a dict with keys:
        emotions       — list of detected emotion labels
        themes         — list of key themes (strings)
        sentiment_score — float in [-1.0, 1.0]

    Falls back gracefully (returns empty result) when the endpoint is unavailable.
    """
    url = os.getenv("JOURNAL_NLP_URL")
    if not url:
        logger.warning("JOURNAL_NLP_URL not set — returning empty NLP analysis")
        return dict(_EMPTY_RESULT)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{url}/analyze",
                json={"text": text},
                headers={"Authorization": f"Bearer {os.getenv('HF_API_TOKEN', '')}"},
            )
            response.raise_for_status()
            data = response.json()
            # Ensure all expected keys are present
            return {
                "emotions": data.get("emotions", []),
                "themes": data.get("themes", []),
                "sentiment_score": float(data.get("sentiment_score", 0.0)),
            }
    except httpx.TimeoutException:
        logger.warning("Journal NLP timed out — returning empty result")
        return dict(_EMPTY_RESULT)
    except Exception as e:
        logger.error(f"Journal NLP error: {e}")
        return dict(_EMPTY_RESULT)

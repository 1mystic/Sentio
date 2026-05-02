import httpx
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def classify_biases(text: str) -> list[dict]:
    """Call the HuggingFace Space bias classifier.

    Returns a list of dicts like:
        [{"bias_id": "...", "bias": "confirmation-bias", "confidence": 0.87, "span": "..."}]

    Falls back gracefully (returns []) when the endpoint is unavailable.
    """
    url = os.getenv("BIAS_CLASSIFIER_URL")
    if not url:
        logger.warning("BIAS_CLASSIFIER_URL not set — skipping bias classification")
        return []

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{url}/classify",
                json={"text": text},
                headers={"Authorization": f"Bearer {os.getenv('HF_API_TOKEN', '')}"},
            )
            response.raise_for_status()
            return response.json().get("biases", [])
    except httpx.TimeoutException:
        logger.warning("Bias classifier timed out — returning empty result")
        return []
    except Exception as e:
        logger.error(f"Bias classifier error: {e}")
        return []

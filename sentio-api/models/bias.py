from pydantic import BaseModel
from typing import Any
from uuid import UUID


class Bias(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    description: str
    example: str
    research_summary: str | None = None
    detection_signals: list[str] | None = None
    related_bias_ids: list[str] | None = None
    severity_weight: float = 1.0


class DetectedBias(BaseModel):
    """A bias detected in a piece of text by the classifier."""
    bias_id: str | None = None
    bias: str | None = None          # slug or label returned by the classifier
    confidence: float = 0.5
    span: str | None = None          # the text excerpt that triggered the detection

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AssessmentQuestion(BaseModel):
    id: int
    text: str
    type: str = "likert5"
    options: list[str]
    reverse_scored: bool = False
    bias_signal: Optional[str] = None


class SubmitAssessmentRequest(BaseModel):
    raw_scores: dict[str, int | float]  # question_id -> answer value
    computed_scores: dict[str, float]   # subscale -> score
    bias_implications: Optional[dict] = None


class AssessmentResult(BaseModel):
    id: str
    user_id: str
    assessment_id: str
    raw_scores: dict
    computed_scores: dict
    bias_implications: Optional[dict]
    completed_at: datetime

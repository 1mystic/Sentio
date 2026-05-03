from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BiasDetection(BaseModel):
    bias_id: Optional[str] = None
    bias: Optional[str] = None  # slug
    confidence: float = Field(..., ge=0.0, le=1.0)
    span: Optional[str] = None  # excerpt from text


class JournalCreate(BaseModel):
    content: str = Field(..., min_length=10, max_length=10000)
    prompt_used: Optional[str] = None
    mood: Optional[str] = None


class JournalUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=10)
    prompt_used: Optional[str] = None
    mood: Optional[str] = None


class JournalEntry(BaseModel):
    id: str
    user_id: str
    content: str
    prompt_used: Optional[str]
    mood: Optional[str]
    sentiment_score: Optional[float]
    detected_biases: list[BiasDetection] = []
    themes: list[str] = []
    emotions: list[dict] = []
    processing_status: str = "pending"
    created_at: datetime
    updated_at: datetime


class JournalReflectionRequest(BaseModel):
    pass  # empty — reflections are generated from the entry content

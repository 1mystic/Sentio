from pydantic import BaseModel, EmailStr
from typing import Any
from datetime import datetime


class Profile(BaseModel):
    id: str
    username: str | None = None
    display_name: str | None = None
    bio: str | None = None
    onboarding_completed: bool = False
    cognitive_style: dict[str, Any] | None = None
    preferences: dict[str, Any] | None = None
    created_at: datetime | None = None


class UserBiasProfile(BaseModel):
    id: str
    user_id: str
    bias_scores: dict[str, float] = {}
    dominant_category: str | None = None
    archetype: str | None = None
    confidence: float | None = None
    sources: dict[str, Any] | None = None
    last_updated: datetime | None = None

from pydantic import BaseModel
from typing import Optional


class BookingRequest(BaseModel):
    message: Optional[str] = None
    requested_at: Optional[str] = None


class TherapistFilter(BaseModel):
    language: Optional[str] = None
    specialization: Optional[str] = None
    format_type: Optional[str] = None
    max_price: Optional[int] = None

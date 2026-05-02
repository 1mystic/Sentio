from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class JournalEntry(BaseModel):
    """Journal entry model"""
    id: str
    user_id: str
    title: Optional[str] = None
    content: str
    mood_score: Optional[int] = None  # 1-10 scale
    emotions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_private: bool = True
    entry_date: date
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Sentiment analysis results
    sentiment_score: Optional[float] = None  # -1 to 1
    sentiment_label: Optional[str] = None  # positive, negative, neutral
    sentiment_confidence: Optional[float] = None
    
    # AI insights
    key_themes: Optional[List[str]] = None
    emotional_indicators: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

class JournalEntryCreate(BaseModel):
    """Journal entry creation model"""
    title: Optional[str] = None
    content: str
    mood_score: Optional[int] = None
    emotions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_private: bool = True
    entry_date: Optional[date] = None

class JournalEntryUpdate(BaseModel):
    """Journal entry update model"""
    title: Optional[str] = None
    content: Optional[str] = None
    mood_score: Optional[int] = None
    emotions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_private: Optional[bool] = None

class JournalEntryResponse(BaseModel):
    """Journal entry response model"""
    id: str
    title: Optional[str] = None
    content: str
    mood_score: Optional[int] = None
    emotions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    entry_date: date
    created_at: datetime
    updated_at: Optional[datetime] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    key_themes: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class JournalEntryList(BaseModel):
    """Journal entry list item"""
    id: str
    title: Optional[str] = None
    content_preview: str  # First 150 characters
    mood_score: Optional[int] = None
    entry_date: date
    created_at: datetime
    sentiment_label: Optional[str] = None
    word_count: int

class JournalAnalytics(BaseModel):
    """Journal analytics model"""
    total_entries: int
    entries_this_week: int
    entries_this_month: int
    average_mood: Optional[float] = None
    mood_trend: Optional[str] = None  # improving, declining, stable
    most_common_emotions: List[Dict[str, Any]]
    most_common_themes: List[Dict[str, Any]]
    sentiment_distribution: Dict[str, int]
    writing_streak: int
    longest_streak: int
    total_words: int

class MoodEntry(BaseModel):
    """Daily mood entry"""
    id: str
    user_id: str
    mood_score: int  # 1-10
    emotions: Optional[List[str]] = None
    notes: Optional[str] = None
    triggers: Optional[List[str]] = None
    entry_date: date
    created_at: datetime

class MoodEntryCreate(BaseModel):
    """Mood entry creation"""
    mood_score: int
    emotions: Optional[List[str]] = None
    notes: Optional[str] = None
    triggers: Optional[List[str]] = None
    entry_date: Optional[date] = None

class JournalPrompt(BaseModel):
    """Journal prompt model"""
    id: str
    title: str
    prompt_text: str
    category: str
    difficulty_level: str  # beginner, intermediate, advanced
    tags: Optional[List[str]] = None
    is_active: bool = True
    created_at: datetime

class JournalPromptResponse(BaseModel):
    """Journal prompt response"""
    id: str
    title: str
    prompt_text: str
    category: str
    difficulty_level: str
    tags: Optional[List[str]] = None

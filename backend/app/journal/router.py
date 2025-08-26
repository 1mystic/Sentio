from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import List, Optional
from datetime import datetime, date
import logging
import uuid

from app.journal.models import (
    JournalEntryCreate, 
    JournalEntryUpdate, 
    JournalEntryResponse,
    JournalEntryList,
    JournalAnalytics,
    MoodEntryCreate,
    JournalPromptResponse
)
from app.journal.sentiment import analyze_journal_entry
from app.auth.models import User
from app.dependencies import get_current_user
from app.database.connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/entries", response_model=List[JournalEntryList])
async def get_journal_entries(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Get user's journal entries"""
    try:
        query = supabase.table("journal_entries").select("*").eq("user_id", current_user.id)
        
        if start_date:
            query = query.gte("entry_date", start_date.isoformat())
        if end_date:
            query = query.lte("entry_date", end_date.isoformat())
            
        entries_response = query.order("entry_date", desc=True).range(offset, offset + limit - 1).execute()
        
        # Format response
        entries = []
        for entry in entries_response.data:
            content_preview = entry["content"][:150] + "..." if len(entry["content"]) > 150 else entry["content"]
            word_count = len(entry["content"].split())
            
            entries.append(JournalEntryList(
                id=entry["id"],
                title=entry.get("title"),
                content_preview=content_preview,
                mood_score=entry.get("mood_score"),
                entry_date=date.fromisoformat(entry["entry_date"]),
                created_at=datetime.fromisoformat(entry["created_at"]),
                sentiment_label=entry.get("sentiment_label"),
                word_count=word_count
            ))
        
        return entries
        
    except Exception as e:
        logger.error(f"Error fetching journal entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch journal entries"
        )

@router.post("/entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Create a new journal entry"""
    try:
        # Analyze the content
        analysis = analyze_journal_entry(entry_data.content)
        
        # Prepare entry data
        entry_id = str(uuid.uuid4())
        entry_record = {
            "id": entry_id,
            "user_id": current_user.id,
            "title": entry_data.title,
            "content": entry_data.content,
            "mood_score": entry_data.mood_score,
            "emotions": entry_data.emotions or [],
            "tags": entry_data.tags or [],
            "is_private": entry_data.is_private,
            "entry_date": (entry_data.entry_date or date.today()).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "sentiment_score": analysis["sentiment_score"],
            "sentiment_label": analysis["sentiment_label"],
            "sentiment_confidence": analysis["sentiment_confidence"],
            "key_themes": analysis["key_themes"],
            "emotional_indicators": analysis["emotional_indicators"],
            "suggestions": analysis["suggestions"]
        }
        
        # Insert into database
        response = supabase.table("journal_entries").insert(entry_record).execute()
        
        if response.data:
            entry = response.data[0]
            return JournalEntryResponse(
                id=entry["id"],
                title=entry.get("title"),
                content=entry["content"],
                mood_score=entry.get("mood_score"),
                emotions=entry.get("emotions", []),
                tags=entry.get("tags", []),
                entry_date=date.fromisoformat(entry["entry_date"]),
                created_at=datetime.fromisoformat(entry["created_at"]),
                updated_at=datetime.fromisoformat(entry["updated_at"]) if entry.get("updated_at") else None,
                sentiment_score=entry.get("sentiment_score"),
                sentiment_label=entry.get("sentiment_label"),
                key_themes=entry.get("key_themes", []),
                suggestions=entry.get("suggestions", [])
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create journal entry"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create journal entry"
        )

@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Get a specific journal entry"""
    try:
        response = supabase.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        entry = response.data[0]
        return JournalEntryResponse(
            id=entry["id"],
            title=entry.get("title"),
            content=entry["content"],
            mood_score=entry.get("mood_score"),
            emotions=entry.get("emotions", []),
            tags=entry.get("tags", []),
            entry_date=date.fromisoformat(entry["entry_date"]),
            created_at=datetime.fromisoformat(entry["created_at"]),
            updated_at=datetime.fromisoformat(entry["updated_at"]) if entry.get("updated_at") else None,
            sentiment_score=entry.get("sentiment_score"),
            sentiment_label=entry.get("sentiment_label"),
            key_themes=entry.get("key_themes", []),
            suggestions=entry.get("suggestions", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching journal entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch journal entry"
        )

@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry_data: JournalEntryUpdate,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Update a journal entry"""
    try:
        # Check if entry exists and belongs to user
        existing_response = supabase.table("journal_entries").select("*").eq("id", entry_id).eq("user_id", current_user.id).execute()
        
        if not existing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        
        # Only update provided fields
        if entry_data.title is not None:
            update_data["title"] = entry_data.title
        if entry_data.content is not None:
            update_data["content"] = entry_data.content
            # Re-analyze sentiment if content changed
            analysis = analyze_journal_entry(entry_data.content)
            update_data.update({
                "sentiment_score": analysis["sentiment_score"],
                "sentiment_label": analysis["sentiment_label"],
                "sentiment_confidence": analysis["sentiment_confidence"],
                "key_themes": analysis["key_themes"],
                "emotional_indicators": analysis["emotional_indicators"],
                "suggestions": analysis["suggestions"]
            })
        if entry_data.mood_score is not None:
            update_data["mood_score"] = entry_data.mood_score
        if entry_data.emotions is not None:
            update_data["emotions"] = entry_data.emotions
        if entry_data.tags is not None:
            update_data["tags"] = entry_data.tags
        if entry_data.is_private is not None:
            update_data["is_private"] = entry_data.is_private
        
        # Update in database
        response = supabase.table("journal_entries").update(update_data).eq("id", entry_id).eq("user_id", current_user.id).execute()
        
        if response.data:
            entry = response.data[0]
            return JournalEntryResponse(
                id=entry["id"],
                title=entry.get("title"),
                content=entry["content"],
                mood_score=entry.get("mood_score"),
                emotions=entry.get("emotions", []),
                tags=entry.get("tags", []),
                entry_date=date.fromisoformat(entry["entry_date"]),
                created_at=datetime.fromisoformat(entry["created_at"]),
                updated_at=datetime.fromisoformat(entry["updated_at"]) if entry.get("updated_at") else None,
                sentiment_score=entry.get("sentiment_score"),
                sentiment_label=entry.get("sentiment_label"),
                key_themes=entry.get("key_themes", []),
                suggestions=entry.get("suggestions", [])
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update journal entry"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating journal entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update journal entry"
        )

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Delete a journal entry"""
    try:
        response = supabase.table("journal_entries").delete().eq("id", entry_id).eq("user_id", current_user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journal entry not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting journal entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete journal entry"
        )

@router.get("/analytics", response_model=JournalAnalytics)
async def get_journal_analytics(
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Get journal analytics for the user"""
    try:
        # This would implement comprehensive analytics
        # For now, returning a basic structure
        return JournalAnalytics(
            total_entries=0,
            entries_this_week=0,
            entries_this_month=0,
            average_mood=None,
            mood_trend=None,
            most_common_emotions=[],
            most_common_themes=[],
            sentiment_distribution={"positive": 0, "negative": 0, "neutral": 0},
            writing_streak=0,
            longest_streak=0,
            total_words=0
        )
        
    except Exception as e:
        logger.error(f"Error fetching journal analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch journal analytics"
        )

@router.get("/prompts", response_model=List[JournalPromptResponse])
async def get_journal_prompts(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    supabase: Client = Depends(get_db)
):
    """Get journal writing prompts"""
    try:
        query = supabase.table("journal_prompts").select("*").eq("is_active", True)
        
        if category:
            query = query.eq("category", category)
        if difficulty:
            query = query.eq("difficulty_level", difficulty)
            
        response = query.limit(limit).execute()
        
        return [JournalPromptResponse(**prompt) for prompt in response.data]
        
    except Exception as e:
        logger.error(f"Error fetching journal prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch journal prompts"
        )

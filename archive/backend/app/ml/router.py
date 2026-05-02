"""
ML Router for FastAPI backend.
Provides endpoints for machine learning services.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from ..auth.dependencies import get_current_user
from ..database import get_db
from .service import ml_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["machine-learning"])

# Pydantic models for request/response

class JournalAnalysisRequest(BaseModel):
    entry_text: str
    entry_metadata: Optional[Dict[str, Any]] = None

class JournalAnalysisResponse(BaseModel):
    user_id: str
    entry_analysis: Dict[str, Any]
    crisis_assessment: Dict[str, Any]
    requires_attention: bool
    analysis_timestamp: str

class PatternAnalysisRequest(BaseModel):
    user_data: List[Dict[str, Any]]
    analysis_period_days: Optional[int] = 30

class PatternAnalysisResponse(BaseModel):
    user_id: str
    patterns: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    analysis_date: str

class MoodPredictionRequest(BaseModel):
    current_context: Dict[str, Any]
    include_historical: Optional[bool] = True

class MoodPredictionResponse(BaseModel):
    user_id: str
    prediction: float
    confidence: float
    factors: List[str]
    prediction_timestamp: str

class RecommendationRequest(BaseModel):
    analysis_results: Dict[str, Any]
    preference_filters: Optional[List[str]] = None

class MLInsightsDashboardResponse(BaseModel):
    user_id: str
    generated_at: str
    insights: Dict[str, Any]

# Endpoints

@router.post("/analyze-journal", response_model=JournalAnalysisResponse)
async def analyze_journal_entry(
    request: JournalAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Analyze a journal entry for sentiment, mental health indicators, and crisis detection.
    """
    try:
        user_id = current_user["id"]
        
        # Perform ML analysis
        analysis_result = await ml_service.analyze_journal_entry(
            entry_text=request.entry_text,
            user_id=user_id,
            entry_metadata=request.entry_metadata
        )
        
        # If crisis is detected, trigger immediate notifications
        if analysis_result.get("requires_attention", False):
            background_tasks.add_task(
                _handle_crisis_detection,
                user_id=user_id,
                analysis_result=analysis_result,
                db=db
            )
        
        return JournalAnalysisResponse(**analysis_result)
        
    except Exception as e:
        logger.error(f"Error in journal analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.post("/analyze-patterns", response_model=PatternAnalysisResponse)
async def analyze_user_patterns(
    request: PatternAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Analyze user behavioral patterns and generate insights.
    """
    try:
        user_id = current_user["id"]
        
        # If no user data provided, fetch from database
        if not request.user_data:
            # This would typically fetch user's journal entries, assessments, etc.
            user_data = await _fetch_user_data_for_analysis(user_id, request.analysis_period_days, db)
        else:
            user_data = request.user_data
        
        # Perform pattern analysis
        pattern_result = await ml_service.analyze_user_patterns(
            user_id=user_id,
            user_data=user_data
        )
        
        return PatternAnalysisResponse(**pattern_result)
        
    except Exception as e:
        logger.error(f"Error in pattern analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Pattern analysis failed")

@router.post("/predict-mood", response_model=MoodPredictionResponse)
async def predict_mood(
    request: MoodPredictionRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Predict user's mood based on current context and historical data.
    """
    try:
        user_id = current_user["id"]
        
        # Fetch historical data if requested
        historical_data = None
        if request.include_historical:
            historical_data = await _fetch_historical_mood_data(user_id, db)
        
        # Make mood prediction
        prediction_result = await ml_service.predict_mood(
            user_id=user_id,
            current_context=request.current_context,
            historical_data=historical_data
        )
        
        return MoodPredictionResponse(**prediction_result)
        
    except Exception as e:
        logger.error(f"Error in mood prediction endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Mood prediction failed")

@router.post("/recommendations")
async def get_personalized_recommendations(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate personalized recommendations based on analysis results.
    """
    try:
        user_id = current_user["id"]
        
        recommendations = await ml_service.generate_personalized_recommendations(
            user_id=user_id,
            analysis_results=request.analysis_results
        )
        
        # Apply preference filters if provided
        if request.preference_filters:
            recommendations = [
                rec for rec in recommendations
                if rec.get("type") in request.preference_filters
            ]
        
        return {"recommendations": recommendations}
        
    except Exception as e:
        logger.error(f"Error in recommendations endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Recommendation generation failed")

@router.get("/insights-dashboard", response_model=MLInsightsDashboardResponse)
async def get_ml_insights_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive ML insights for user dashboard.
    """
    try:
        user_id = current_user["id"]
        
        dashboard_data = await ml_service.get_ml_insights_dashboard(user_id)
        
        return MLInsightsDashboardResponse(**dashboard_data)
        
    except Exception as e:
        logger.error(f"Error in ML insights dashboard endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Dashboard generation failed")

@router.get("/detect-concerning-patterns")
async def detect_concerning_patterns(
    days: int = 7,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Detect concerning patterns that might require intervention.
    """
    try:
        user_id = current_user["id"]
        
        # Fetch recent entries
        recent_entries = await _fetch_recent_entries(user_id, days, db)
        
        # Detect concerning patterns
        pattern_analysis = await ml_service.detect_concerning_patterns(
            user_id=user_id,
            recent_entries=recent_entries
        )
        
        return pattern_analysis
        
    except Exception as e:
        logger.error(f"Error in concerning patterns detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Pattern detection failed")

@router.get("/crisis-resources")
async def get_crisis_resources():
    """
    Get crisis resources and helplines.
    """
    try:
        resources = [
            {
                "name": "National Suicide Prevention Lifeline",
                "phone": "988",
                "description": "24/7 crisis support",
                "website": "https://suicidepreventionlifeline.org/",
                "type": "crisis_hotline"
            },
            {
                "name": "Crisis Text Line",
                "phone": "Text HOME to 741741",
                "description": "24/7 text-based crisis support",
                "website": "https://www.crisistextline.org/",
                "type": "text_support"
            },
            {
                "name": "SAMHSA National Helpline",
                "phone": "1-800-662-4357",
                "description": "Treatment referral and information service",
                "website": "https://www.samhsa.gov/find-help/national-helpline",
                "type": "treatment_referral"
            },
            {
                "name": "National Alliance on Mental Illness (NAMI)",
                "phone": "1-800-950-6264",
                "description": "Support and information for mental health",
                "website": "https://www.nami.org/",
                "type": "support_organization"
            }
        ]
        
        return {"crisis_resources": resources}
        
    except Exception as e:
        logger.error(f"Error fetching crisis resources: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch crisis resources")

@router.post("/train-personal-model")
async def train_personal_model(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Train a personalized ML model for the user based on their historical data.
    """
    try:
        user_id = current_user["id"]
        
        # Add training task to background
        background_tasks.add_task(
            _train_user_specific_model,
            user_id=user_id,
            db=db
        )
        
        return {
            "message": "Personal model training initiated",
            "user_id": user_id,
            "status": "training_started"
        }
        
    except Exception as e:
        logger.error(f"Error initiating model training: {str(e)}")
        raise HTTPException(status_code=500, detail="Model training failed to start")

@router.get("/model-status")
async def get_model_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get the status of the user's personalized ML models.
    """
    try:
        user_id = current_user["id"]
        
        # This would check the status of various models for the user
        status = {
            "user_id": user_id,
            "models": {
                "mood_predictor": {
                    "status": "trained",
                    "accuracy": 0.85,
                    "last_updated": "2024-01-15T10:30:00Z",
                    "training_data_points": 150
                },
                "sentiment_analyzer": {
                    "status": "active",
                    "version": "2.1.0",
                    "last_updated": "2024-01-10T14:20:00Z"
                },
                "pattern_detector": {
                    "status": "training",
                    "progress": 0.75,
                    "estimated_completion": "2024-01-16T09:00:00Z"
                }
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error fetching model status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch model status")

# Background task functions

async def _handle_crisis_detection(user_id: str, analysis_result: Dict[str, Any], db):
    """Handle crisis detection by notifying appropriate parties."""
    try:
        logger.warning(f"Crisis detected for user {user_id}")
        
        # In a real implementation, this would:
        # 1. Send immediate notifications to emergency contacts
        # 2. Alert mental health professionals
        # 3. Log the incident for follow-up
        # 4. Potentially trigger automated safety protocols
        
        # For now, we'll just log the incident
        crisis_log = {
            "user_id": user_id,
            "crisis_detected_at": analysis_result.get("analysis_timestamp"),
            "risk_score": analysis_result.get("crisis_assessment", {}).get("risk_score", 0),
            "crisis_indicators": analysis_result.get("crisis_assessment", {}).get("crisis_indicators", []),
            "status": "logged"
        }
        
        logger.info(f"Crisis incident logged: {crisis_log}")
        
    except Exception as e:
        logger.error(f"Error handling crisis detection: {str(e)}")

async def _train_user_specific_model(user_id: str, db):
    """Train user-specific ML models in the background."""
    try:
        logger.info(f"Starting model training for user {user_id}")
        
        # Fetch user's historical data
        historical_data = await _fetch_comprehensive_user_data(user_id, db)
        
        if len(historical_data) < 10:
            logger.warning(f"Insufficient data for training user {user_id} model")
            return
        
        # Train mood prediction model
        success = await ml_service.mood_predictor.train(historical_data)
        
        if success:
            logger.info(f"Model training completed successfully for user {user_id}")
        else:
            logger.error(f"Model training failed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in background model training: {str(e)}")

# Helper functions for database operations

async def _fetch_user_data_for_analysis(user_id: str, days: int, db) -> List[Dict[str, Any]]:
    """Fetch user data for pattern analysis."""
    # Placeholder - would implement actual database queries
    return [
        {
            "id": 1,
            "user_id": user_id,
            "content": "Sample journal entry",
            "sentiment_score": 0.5,
            "created_at": "2024-01-15T10:00:00Z",
            "type": "journal_entry"
        }
    ]

async def _fetch_historical_mood_data(user_id: str, db) -> List[Dict[str, Any]]:
    """Fetch historical mood data for prediction model."""
    # Placeholder - would implement actual database queries
    return [
        {
            "day_of_week": 1,
            "hour_of_day": 10,
            "previous_mood": 3.5,
            "sentiment_trend": 0.2,
            "entry_frequency": 1.2,
            "sleep_quality": 4.0,
            "activity_level": 3.5,
            "mood_score": 3.8
        }
    ]

async def _fetch_recent_entries(user_id: str, days: int, db) -> List[Dict[str, Any]]:
    """Fetch recent entries for pattern detection."""
    # Placeholder - would implement actual database queries
    return [
        {
            "id": 1,
            "user_id": user_id,
            "content": "Recent journal entry",
            "sentiment_score": 0.3,
            "crisis_detected": False,
            "created_at": "2024-01-15T10:00:00Z"
        }
    ]

async def _fetch_comprehensive_user_data(user_id: str, db) -> List[Dict[str, Any]]:
    """Fetch comprehensive user data for model training."""
    # Placeholder - would implement actual database queries combining
    # journal entries, assessments, mood ratings, etc.
    return []

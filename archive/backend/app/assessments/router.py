from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import List, Optional
from datetime import datetime
import logging
import uuid

from app.assessments.models import (
    AssessmentListResponse, 
    AssessmentDetailResponse, 
    AssessmentSubmission,
    AssessmentResultResponse,
    AssessmentResult,
    AssessmentStatus
)
from app.assessments.scoring import score_assessment
from app.auth.models import User
from app.dependencies import get_current_user
from app.database.connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[AssessmentListResponse])
async def get_assessments(
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Get list of available assessments for the user"""
    try:
        # Get assessments
        query = supabase.table("assessments").select("*").eq("is_active", True)
        
        if category:
            query = query.eq("category", category)
            
        assessments_response = query.execute()
        
        # Get user's progress for each assessment
        user_progress = supabase.table("assessment_progress").select("*").eq("user_id", current_user.id).execute()
        progress_map = {p["assessment_id"]: p for p in user_progress.data}
        
        # Get user's results for completed assessments
        user_results = supabase.table("assessment_results").select("*").eq("user_id", current_user.id).execute()
        results_map = {}
        for result in user_results.data:
            assessment_id = result["assessment_id"]
            if assessment_id not in results_map or result["completed_at"] > results_map[assessment_id]["completed_at"]:
                results_map[assessment_id] = result
        
        # Format response
        response = []
        for assessment in assessments_response.data:
            progress = progress_map.get(assessment["id"])
            result = results_map.get(assessment["id"])
            
            status = AssessmentStatus.NOT_STARTED
            if progress:
                status = AssessmentStatus(progress["status"])
            elif result:
                status = AssessmentStatus.COMPLETED
            
            response.append(AssessmentListResponse(
                id=assessment["id"],
                title=assessment["title"],
                description=assessment["description"],
                category=assessment["category"],
                estimated_time=assessment["estimated_time"],
                status=status,
                last_taken=result["completed_at"] if result else None,
                best_score=result["score"] if result else None
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching assessments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessments"
        )

@router.get("/{assessment_id}", response_model=AssessmentDetailResponse)
async def get_assessment_detail(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Get detailed assessment information including questions"""
    try:
        # Get assessment
        assessment_response = supabase.table("assessments").select("*").eq("id", assessment_id).eq("is_active", True).execute()
        
        if not assessment_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        assessment = assessment_response.data[0]
        
        # Get questions for this assessment
        questions_response = supabase.table("assessment_questions").select("*").eq("assessment_id", assessment_id).order("order_index").execute()
        
        # Get user's progress
        progress_response = supabase.table("assessment_progress").select("*").eq("user_id", current_user.id).eq("assessment_id", assessment_id).execute()
        
        progress = progress_response.data[0] if progress_response.data else None
        
        return AssessmentDetailResponse(
            id=assessment["id"],
            title=assessment["title"],
            description=assessment["description"],
            assessment_type=assessment["assessment_type"],
            category=assessment["category"],
            estimated_time=assessment["estimated_time"],
            instructions=assessment.get("instructions"),
            questions=questions_response.data,
            total_questions=len(questions_response.data),
            user_progress=progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessment detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessment details"
        )

@router.post("/{assessment_id}/submit", response_model=AssessmentResultResponse)
async def submit_assessment(
    assessment_id: str,
    submission: AssessmentSubmission,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Submit assessment responses and get results"""
    try:
        # Validate assessment exists
        assessment_response = supabase.table("assessments").select("*").eq("id", assessment_id).eq("is_active", True).execute()
        
        if not assessment_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        assessment = assessment_response.data[0]
        
        # Process responses
        responses_dict = {resp.question_id: resp.answer for resp in submission.responses}
        
        # Score the assessment
        scoring_result = score_assessment(assessment["assessment_type"], responses_dict)
        
        # Save result
        result_id = str(uuid.uuid4())
        result_data = {
            "id": result_id,
            "user_id": current_user.id,
            "assessment_id": assessment_id,
            "score": scoring_result.get("score"),
            "max_score": scoring_result.get("max_score"),
            "percentage": scoring_result.get("percentage"),
            "interpretation": scoring_result.get("interpretation"),
            "recommendations": scoring_result.get("recommendations"),
            "risk_level": scoring_result.get("risk_level"),
            "responses": responses_dict,
            "completed_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result_response = supabase.table("assessment_results").insert(result_data).execute()
        
        # Update or delete progress
        supabase.table("assessment_progress").delete().eq("user_id", current_user.id).eq("assessment_id", assessment_id).execute()
        
        # Return result
        return AssessmentResultResponse(
            id=result_id,
            assessment=assessment,
            score=scoring_result.get("score"),
            max_score=scoring_result.get("max_score"),
            percentage=scoring_result.get("percentage"),
            interpretation=scoring_result.get("interpretation"),
            recommendations=scoring_result.get("recommendations"),
            risk_level=scoring_result.get("risk_level"),
            completed_at=datetime.fromisoformat(result_data["completed_at"]),
            insights=scoring_result  # Include full scoring result as insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit assessment"
        )

@router.get("/results/", response_model=List[AssessmentResultResponse])
async def get_user_results(
    assessment_type: Optional[str] = Query(None, description="Filter by assessment type"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return"),
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Get user's assessment results"""
    try:
        # Build query
        query = supabase.table("assessment_results").select("*, assessments!inner(*)").eq("user_id", current_user.id)
        
        if assessment_type:
            query = query.eq("assessments.assessment_type", assessment_type)
        
        results_response = query.order("completed_at", desc=True).limit(limit).execute()
        
        # Format response
        response = []
        for result in results_response.data:
            response.append(AssessmentResultResponse(
                id=result["id"],
                assessment=result["assessments"],
                score=result["score"],
                max_score=result["max_score"],
                percentage=result["percentage"],
                interpretation=result["interpretation"],
                recommendations=result["recommendations"],
                risk_level=result["risk_level"],
                completed_at=datetime.fromisoformat(result["completed_at"]),
                insights={"responses": result["responses"]}
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching user results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessment results"
        )

@router.get("/results/{result_id}", response_model=AssessmentResultResponse)
async def get_result_detail(
    result_id: str,
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_db)
):
    """Get detailed assessment result"""
    try:
        result_response = supabase.table("assessment_results").select("*, assessments!inner(*)").eq("id", result_id).eq("user_id", current_user.id).execute()
        
        if not result_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment result not found"
            )
        
        result = result_response.data[0]
        
        return AssessmentResultResponse(
            id=result["id"],
            assessment=result["assessments"],
            score=result["score"],
            max_score=result["max_score"],
            percentage=result["percentage"],
            interpretation=result["interpretation"],
            recommendations=result["recommendations"],
            risk_level=result["risk_level"],
            completed_at=datetime.fromisoformat(result["completed_at"]),
            insights={"responses": result["responses"]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching result detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessment result"
        )

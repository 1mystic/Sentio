from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class AssessmentType(str, Enum):
    GAD7 = "gad7"
    PHQ9 = "phq9"
    COGNITIVE_BIAS = "cognitive_bias"
    VALUES = "values"
    STRESS = "stress"

class AssessmentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    TEXT = "text"
    BOOLEAN = "boolean"

class Assessment(BaseModel):
    """Assessment model"""
    id: str
    title: str
    description: str
    assessment_type: AssessmentType
    category: str
    estimated_time: str
    instructions: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

class Question(BaseModel):
    """Question model"""
    id: str
    assessment_id: str
    question_text: str
    question_type: QuestionType
    order_index: int
    is_required: bool = True
    options: Optional[List[Dict[str, Any]]] = None  # For multiple choice questions
    min_value: Optional[int] = None  # For scale questions
    max_value: Optional[int] = None  # For scale questions
    scale_labels: Optional[Dict[str, str]] = None  # For scale questions

class AssessmentResponse(BaseModel):
    """Individual question response"""
    question_id: str
    answer: Any  # Can be string, int, bool, etc.
    response_time: Optional[int] = None  # Time taken to answer in seconds

class AssessmentSubmission(BaseModel):
    """Assessment submission"""
    assessment_id: str
    responses: List[AssessmentResponse]

class AssessmentResult(BaseModel):
    """Assessment result"""
    id: str
    user_id: str
    assessment_id: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    percentage: Optional[float] = None
    interpretation: Optional[str] = None
    recommendations: Optional[List[str]] = None
    risk_level: Optional[str] = None  # low, moderate, high
    responses: Dict[str, Any]
    completed_at: datetime
    created_at: datetime

class AssessmentProgress(BaseModel):
    """User's assessment progress"""
    user_id: str
    assessment_id: str
    status: AssessmentStatus
    current_question: Optional[int] = None
    total_questions: int
    responses: Dict[str, Any] = {}
    started_at: Optional[datetime] = None
    last_updated: datetime

# Response models
class AssessmentListResponse(BaseModel):
    """Assessment list response"""
    id: str
    title: str
    description: str
    category: str
    estimated_time: str
    status: AssessmentStatus
    last_taken: Optional[datetime] = None
    best_score: Optional[float] = None

class AssessmentDetailResponse(BaseModel):
    """Assessment detail response"""
    id: str
    title: str
    description: str
    assessment_type: AssessmentType
    category: str
    estimated_time: str
    instructions: Optional[str] = None
    questions: List[Question]
    total_questions: int
    user_progress: Optional[AssessmentProgress] = None

class AssessmentResultResponse(BaseModel):
    """Assessment result response"""
    id: str
    assessment: Assessment
    score: Optional[float] = None
    max_score: Optional[float] = None
    percentage: Optional[float] = None
    interpretation: Optional[str] = None
    recommendations: Optional[List[str]] = None
    risk_level: Optional[str] = None
    completed_at: datetime
    insights: Optional[Dict[str, Any]] = None  # ML-generated insights

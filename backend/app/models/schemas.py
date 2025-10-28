from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    ALGEBRA = "algebra"
    CALCULUS = "calculus"
    GEOMETRY = "geometry"
    STATISTICS = "statistics"
    TRIGONOMETRY = "trigonometry"
    LINEAR_ALGEBRA = "linear_algebra"
    OTHER = "other"

class RouteType(str, Enum):
    KNOWLEDGE_BASE = "knowledge_base"
    WEB_SEARCH = "web_search"
    HYBRID = "hybrid"

class MathQuestion(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    topic: Optional[QuestionType] = None
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    context: Optional[str] = None

class GuardrailsResult(BaseModel):
    is_valid: bool
    reason: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class KnowledgeBaseResult(BaseModel):
    found: bool
    content: Optional[str] = None
    similarity_score: Optional[float] = None
    source: Optional[str] = None

class WebSearchResult(BaseModel):
    found: bool
    content: Optional[str] = None
    sources: List[str] = []
    search_query: Optional[str] = None

class StepByStepSolution(BaseModel):
    steps: List[str]
    explanation: str
    final_answer: str
    difficulty_assessment: str

class MathResponse(BaseModel):
    question: str
    solution: StepByStepSolution
    route_used: RouteType
    confidence_score: float
    sources: List[str] = []
    response_time: float
    timestamp: datetime

class FeedbackRequest(BaseModel):
    response_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
    is_helpful: bool
    suggested_improvement: Optional[str] = None

class FeedbackResponse(BaseModel):
    message: str
    feedback_id: str
    status: str

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, bool]
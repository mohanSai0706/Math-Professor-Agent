import logging
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.schemas import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        self.feedback_storage = {}  # In production, use a database
    
    async def process_feedback(
        self, 
        feedback: FeedbackRequest,
        original_question: str,
        original_solution: str
    ) -> FeedbackResponse:
        """Process user feedback and improve the system."""
        try:
            feedback_id = str(uuid.uuid4())
            
            # Store feedback
            self.feedback_storage[feedback_id] = {
                "feedback": feedback.dict(),
                "original_question": original_question,
                "original_solution": original_solution,
                "timestamp": datetime.utcnow(),
                "processed": True
            }
            
            logger.info(f"Processed feedback: {feedback_id} with rating {feedback.rating}")
            
            return FeedbackResponse(
                message="Thank you for your feedback! We'll use it to improve our responses.",
                feedback_id=feedback_id,
                status="processed"
            )
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return FeedbackResponse(
                message="Error processing feedback. Please try again.",
                feedback_id="",
                status="error"
            )
    
    async def get_feedback_analytics(self) -> Dict[str, Any]:
        """Get analytics about feedback received."""
        try:
            total_feedback = len(self.feedback_storage)
            if total_feedback == 0:
                return {"total": 0}
            
            ratings = [
                feedback["feedback"]["rating"] 
                for feedback in self.feedback_storage.values()
            ]
            helpful_count = sum(
                1 for feedback in self.feedback_storage.values() 
                if feedback["feedback"]["is_helpful"]
            )
            
            analytics = {
                "total_feedback": total_feedback,
                "average_rating": sum(ratings) / len(ratings) if ratings else 0,
                "helpful_percentage": (helpful_count / total_feedback) * 100 if total_feedback > 0 else 0,
                "rating_distribution": {
                    str(i): ratings.count(i) for i in range(1, 6)
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting feedback analytics: {str(e)}")
            return {"error": "Unable to fetch analytics"}
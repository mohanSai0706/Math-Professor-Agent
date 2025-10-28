import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.core.config import settings
from app.core.routing import MathRoutingAgent
from app.models.schemas import (
    MathQuestion, MathResponse, FeedbackRequest, FeedbackResponse, HealthCheck
)
from app.services.knowledge_base import KnowledgeBaseService
from app.services.feedback import FeedbackService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
routing_agent = None
feedback_service = None
knowledge_base_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global routing_agent, feedback_service, knowledge_base_service
    
    logger.info("Starting Math Routing Agent...")
    
    # Initialize services
    try:
        knowledge_base_service = KnowledgeBaseService()
        await knowledge_base_service.initialize_collection()
        
        routing_agent = MathRoutingAgent()
        feedback_service = FeedbackService()
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Math Routing Agent...")

# Create FastAPI app
app = FastAPI(
    title="Math Routing Agent",
    description="Agentic-RAG Mathematical Professor System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    try:
        services_status = {
            "routing_agent": routing_agent is not None,
            "knowledge_base": knowledge_base_service is not None,
            "feedback_service": feedback_service is not None
        }
        
        return HealthCheck(
            status="healthy" if all(services_status.values()) else "degraded",
            timestamp=datetime.utcnow(),
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheck(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            services={"error": str(e)}
        )

# Main question processing endpoint
@app.post("/ask", response_model=MathResponse)
async def ask_question(question: MathQuestion):
    """Process a mathematical question and return a step-by-step solution."""
    try:
        if not routing_agent:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        logger.info(f"Received question: {question.question[:100]}...")
        
        response = await routing_agent.process_question(question)
        
        logger.info(f"Question processed successfully using {response.route_used} route")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Feedback endpoint
@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback_request: FeedbackRequest,
    background_tasks: BackgroundTasks
):
    """Submit feedback for a response."""
    try:
        if not feedback_service:
            raise HTTPException(status_code=503, detail="Feedback service not ready")
        
        original_question = "Sample question"
        original_solution = "Sample solution"
        
        response = await feedback_service.process_feedback(
            feedback_request,
            original_question,
            original_solution
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing feedback")

# Get feedback analytics
@app.get("/analytics/feedback")
async def get_feedback_analytics():
    """Get feedback analytics."""
    try:
        if not feedback_service:
            raise HTTPException(status_code=503, detail="Feedback service not ready")
        
        analytics = await feedback_service.get_feedback_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting analytics")

# Get knowledge base stats
@app.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """Get knowledge base statistics."""
    try:
        if not knowledge_base_service:
            raise HTTPException(status_code=503, detail="Knowledge base service not ready")
        
        points = await knowledge_base_service.get_all_points()
        return {
            "total_problems": len(points),
            "collection_name": knowledge_base_service.collection_name
        }
        
    except Exception as e:
        logger.error(f"Error getting KB stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting knowledge base stats")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )

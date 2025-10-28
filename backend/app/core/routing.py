import logging
import time
from datetime import datetime
from typing import Optional, Tuple
from app.models.schemas import (
    MathQuestion, MathResponse, RouteType, StepByStepSolution,
    GuardrailsResult, KnowledgeBaseResult, WebSearchResult
)
from app.services.guardrails import GuardrailsService
from app.services.knowledge_base import KnowledgeBaseService
from app.services.web_search import WebSearchService
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class MathRoutingAgent:
    def __init__(self):
        self.guardrails = GuardrailsService()
        self.knowledge_base = KnowledgeBaseService()
        self.web_search = WebSearchService()
        self.gemini = GeminiService()
    
    async def process_question(self, question: MathQuestion) -> MathResponse:
        """Main routing logic for processing mathematical questions."""
        start_time = time.time()
        
        try:
            # Step 1: Input Guardrails
            logger.info(f"Processing question: {question.question[:50]}...")
            
            input_validation = await self.guardrails.validate_input(question)
            if not input_validation.is_valid:
                raise ValueError(f"Input validation failed: {input_validation.reason}")
            
            # Step 2: Route Decision
            route_used, solution, sources, confidence = await self._route_and_solve(question)
            
            # Step 3: Output Guardrails
            solution_text = f"{solution.explanation} {' '.join(solution.steps)} {solution.final_answer}"
            output_validation = await self.guardrails.validate_output(solution_text)
            
            if not output_validation.is_valid:
                logger.warning(f"Output validation warning: {output_validation.reason}")
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Create response
            response = MathResponse(
                question=question.question,
                solution=solution,
                route_used=route_used,
                confidence_score=confidence,
                sources=sources,
                response_time=response_time,
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"Successfully processed question using {route_used} route in {response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            # Return error response
            return MathResponse(
                question=question.question,
                solution=StepByStepSolution(
                    steps=[f"Error: {str(e)}"],
                    explanation="An error occurred while processing your question.",
                    final_answer="Please try rephrasing your question.",
                    difficulty_assessment="unknown"
                ),
                route_used=RouteType.HYBRID,
                confidence_score=0.0,
                sources=[],
                response_time=time.time() - start_time,
                timestamp=datetime.utcnow()
            )
    
    async def _route_and_solve(
        self, 
        question: MathQuestion
    ) -> Tuple[RouteType, StepByStepSolution, list, float]:
        """Route the question and generate solution."""
        
        # Try Knowledge Base first (Primary Route)
        kb_result = await self.knowledge_base.search_knowledge_base(question.question)
        
        similarity_score = kb_result.similarity_score if kb_result.similarity_score is not None else 0.0
        if kb_result.found and similarity_score > 0.8:
            # High confidence knowledge base match
            logger.info(f"Using knowledge base route (similarity: {similarity_score:.3f})")
            
            solution = await self.gemini.generate_solution(
                question.question,
                context=question.context,
                source_material=kb_result.content
            )
            
            return (
                RouteType.KNOWLEDGE_BASE,
                solution,
                [kb_result.source],
                similarity_score
            )
        
        elif kb_result.found and similarity_score > 0.6:
            # Medium confidence - use hybrid approach
            logger.info(f"Using hybrid route (KB similarity: {similarity_score:.3f})")
            
            # Also search web for additional context
            web_result = await self.web_search.search_mathematics(question.question)
            
            # Combine knowledge base and web search content
            combined_context = ""
            sources = []
            
            if kb_result.content:
                combined_context += f"Knowledge Base: {kb_result.content}\n\n"
                sources.append(kb_result.source)
            
            if web_result.found and web_result.content:
                combined_context += f"Web Search: {web_result.content}"
                sources.extend(web_result.sources)
            
            solution = await self.gemini.generate_solution(
                question.question,
                context=question.context,
                source_material=combined_context
            )
            
            # Average confidence from both sources
            confidence = (similarity_score + (0.7 if web_result.found else 0.3)) / 2
            
            return (RouteType.HYBRID, solution, sources, confidence)
        
        else:
            # Low confidence or not found in KB - use web search
            logger.info("Using web search route")
            
            web_result = await self.web_search.search_mathematics(question.question)
            
            if web_result.found:
                solution = await self.gemini.generate_solution(
                    question.question,
                    context=question.context,
                    source_material=web_result.content
                )
                
                return (
                    RouteType.WEB_SEARCH,
                    solution,
                    web_result.sources,
                    0.7  # Default confidence for web search
                )
            else:
                # Fallback - generate solution without external sources
                logger.info("No external sources found, using OpenAI only")
                
                solution = await self.gemini.generate_solution(
                    question.question,
                    context=question.context
                )
                
                return (
                    RouteType.WEB_SEARCH,
                    solution,
                    ["OpenAI GPT-4"],
                    0.5  # Lower confidence without sources
                )
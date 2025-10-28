import re
import logging
from typing import List, Dict, Any
from app.models.schemas import GuardrailsResult, MathQuestion
from app.core.config import settings

logger = logging.getLogger(__name__)

class GuardrailsService:
    def __init__(self):
        self.math_keywords = [
            'solve', 'calculate', 'find', 'equation', 'formula', 'theorem',
            'proof', 'derivative', 'integral', 'limit', 'matrix', 'vector',
            'angle', 'area', 'volume', 'probability', 'statistics', 'graph',
            'function', 'polynomial', 'logarithm', 'exponential', 'trigonometry',
            'circle', 'radius', 'perimeter', 'geometry', 'area', 'volume', 'shape',
            'length', 'width', 'height', 'distance', 'arc', 'sector', 'diameter',
            'circumference', 'rectangle', 'square', 'triangle', 'polygon', 'ellipse',
            'sphere', 'cube', 'cylinder', 'cone', 'pyramid', 'surface', 'solid',
            'dimension', 'coordinate', 'axis', 'plane', 'line', 'segment', 'point',
            'angle', 'degree', 'radian', 'pi', 'π'
        ]
        
        self.prohibited_content = [
            'illegal', 'harmful', 'violence', 'hate', 'discrimination',
            'personal information', 'private data', 'password', 'credit card'
        ]
    
    async def validate_input(self, question: MathQuestion) -> GuardrailsResult:
        """Validate input question for mathematical content and safety."""
        try:
            # Check question length
            if len(question.question) > settings.max_question_length:
                return GuardrailsResult(
                    is_valid=False,
                    reason=f"Question too long. Maximum {settings.max_question_length} characters allowed.",
                    confidence_score=1.0
                )
            
            # Check for prohibited content
            question_lower = question.question.lower()
            for prohibited in self.prohibited_content:
                if prohibited in question_lower:
                    return GuardrailsResult(
                        is_valid=False,
                        reason=f"Prohibited content detected: {prohibited}",
                        confidence_score=0.9
                    )
            
            # Check for mathematical content
            math_score = self._calculate_math_relevance(question.question)
            
            if math_score < 0.0:
                return GuardrailsResult(
                    is_valid=False,
                    reason="Question does not appear to be mathematics-related.",
                    confidence_score=math_score
                )
            
            return GuardrailsResult(
                is_valid=True,
                reason="Question passed all guardrails checks.",
                confidence_score=math_score
            )
            
        except Exception as e:
            logger.error(f"Error in input validation: {str(e)}")
            return GuardrailsResult(
                is_valid=False,
                reason="Internal validation error.",
                confidence_score=0.0
            )
    
    async def validate_output(self, response_content: str) -> GuardrailsResult:
        """Validate output response for safety and quality."""
        try:
            # Check for harmful content
            response_lower = response_content.lower()
            for prohibited in self.prohibited_content:
                if prohibited in response_lower:
                    return GuardrailsResult(
                        is_valid=False,
                        reason=f"Prohibited content in response: {prohibited}",
                        confidence_score=0.9
                    )
            
            # Check response quality (basic checks)
            if len(response_content.strip()) < 20:
                return GuardrailsResult(
                    is_valid=False,
                    reason="Response too short or incomplete.",
                    confidence_score=0.7
                )
            
            # Check for mathematical solution structure
            solution_indicators = ['step', 'solution', 'answer', 'therefore', 'thus', 'result']
            has_solution_structure = any(indicator in response_lower for indicator in solution_indicators)
            
            confidence = 0.8 if has_solution_structure else 0.6
            
            return GuardrailsResult(
                is_valid=True,
                reason="Response passed output validation.",
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Error in output validation: {str(e)}")
            return GuardrailsResult(
                is_valid=False,
                reason="Internal validation error.",
                confidence_score=0.0
            )
    
    def _calculate_math_relevance(self, question: str) -> float:
        """Calculate how relevant the question is to mathematics."""
        question_lower = question.lower()
        
        # Count mathematical keywords
        keyword_count = sum(1 for keyword in self.math_keywords if keyword in question_lower)
        
        # Check for mathematical symbols and patterns
        math_symbols = r'[+\-*/=<>≤≥∑∫∏√∆∇∂]'
        symbol_count = len(re.findall(math_symbols, question))
        
        # Check for numbers and mathematical expressions
        number_pattern = r'\b\d+\.?\d*\b'
        number_count = len(re.findall(number_pattern, question))
        
        # Calculate relevance score
        keyword_score = min(keyword_count * 0.2, 1.0)
        symbol_score = min(symbol_count * 0.1, 0.5)
        number_score = min(number_count * 0.05, 0.3)
        
        total_score = keyword_score + symbol_score + number_score
        return min(total_score, 1.0)
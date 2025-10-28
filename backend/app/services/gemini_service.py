import logging
import asyncio
import time
from typing import List, Dict, Any, Optional

# Assuming these are your project's modules
from app.core.config import settings
from app.models.schemas import StepByStepSolution, MathQuestion

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.api_core import exceptions

logger = logging.getLogger(__name__)

class GeminiService:
    """
    A service class to interact with the Google Gemini API for solving math problems.
    """
    def __init__(self):
        """
        Initializes the Gemini Service by configuring the API key and creating a model instance.
        """
        try:
            # Configure the Gemini API with the key from settings
            genai.configure(api_key=settings.gemini_api_key)
            
            # --- EDITED FOR RATE LIMITING ---
            # Switched to 'gemini-1.5-flash'. This model is much faster and has a significantly
            # more generous free tier, which should resolve the 429 quota errors for development.
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            logger.info("Gemini service initialized successfully with model 'gemini-1.5-flash'")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            # Raise an exception to prevent the application from running with a misconfigured service.
            raise Exception(f"Gemini API configuration failed: {str(e)}")

    async def generate_solution(
        self,
        question: str,
        context: Optional[str] = None,
        source_material: Optional[str] = None
    ) -> StepByStepSolution:
        """
        Generates a full step-by-step solution for a given math question.
        """
        try:
            # Construct the full prompt from system and user parts
            system_prompt = self._get_math_professor_prompt()
            user_prompt = self._create_user_prompt(question, context, source_material)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate content using the corrected async helper method
            response = await self._generate_content_async(full_prompt)
            
            # Extract and parse the response text
            solution_text = self._extract_response_text(response)
            return self._parse_solution(solution_text)
            
        except Exception as e:
            logger.error(f"Error generating solution with Gemini: {str(e)}")
            # Return a structured error response
            return StepByStepSolution(
                steps=[f"Error occurred: {str(e)}", "Please try rephrasing your question."],
                explanation="An error occurred while generating the solution.",
                final_answer="Unable to provide solution due to technical error.",
                difficulty_assessment="intermediate"
            )

    async def assess_question_difficulty(self, question: str) -> str:
        """Assess the difficulty level of a mathematical question."""
        try:
            prompt = f"""
            As a mathematics professor, assess the difficulty level of this question:
            
            Question: {question}
            
            Respond with only one word: "beginner", "intermediate", or "advanced"
            """
            
            # Generate a response with specific, restrictive settings for a single-word answer
            response = await self._generate_content_async(
                prompt, 
                max_tokens=20,
                temperature=0.1
            )
            
            response_text = self._extract_response_text(response)
            difficulty = response_text.strip().lower()
            
            # Validate the response to ensure it's one of the expected values
            return self._validate_difficulty(difficulty)
            
        except Exception as e:
            logger.error(f"Error assessing difficulty with Gemini: {str(e)}")
            # Default to "intermediate" on error
            return "intermediate"

    async def improve_response_with_feedback(
        self, 
        original_question: str,
        original_solution: str,
        feedback: str
    ) -> StepByStepSolution:
        """Improve the solution based on human feedback."""
        try:
            prompt = f"""
            As a mathematics professor, improve this solution based on the feedback:
            
            Original Question: {original_question}
            Original Solution: {original_solution}
            Feedback: {feedback}
            
            Please provide an improved step-by-step solution that addresses the feedback.
            Format your response exactly as specified in the system prompt.
            """
            
            response = await self._generate_content_async(prompt)
            solution_text = self._extract_response_text(response)
            
            return self._parse_solution(solution_text)
            
        except Exception as e:
            logger.error(f"Error improving solution with Gemini: {str(e)}")
            raise Exception(f"Failed to improve solution: {str(e)}")

    async def _generate_content_async(
        self, 
        prompt: str, 
        max_tokens: int = 2000, 
        temperature: float = 0.3
    ) -> Any:
        """
        A helper method to generate content asynchronously.
        Includes exponential backoff to handle rate limit errors gracefully.
        """
        # Define the generation configuration
        config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=0.8,
            top_k=40
        )
        
        # --- EDITED FOR RATE LIMITING ---
        # Added a retry loop with exponential backoff for resilience.
        max_retries = 3
        delay = 1  # Initial delay in seconds
        for attempt in range(max_retries):
            try:
                response = await self.model.generate_content_async(
                    contents=prompt,
                    generation_config=config
                )
                return response
            except exceptions.ResourceExhausted as e:
                logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
                delay *= 2  # Double the delay for the next attempt
            except Exception as e:
                logger.error(f"An unexpected error occurred in async content generation: {str(e)}")
                raise # Re-raise other unexpected errors
        
        # If all retries fail, raise the last error
        raise Exception("API request failed after multiple retries due to rate limiting.")


    def test_connection(self) -> bool:
        """Test if Gemini API connection is working using a synchronous call."""
        try:
            config = GenerationConfig(temperature=0.1, max_output_tokens=10)
            
            # CORRECTED: Call generate_content on the self.model instance
            test_response = self.model.generate_content(
                contents="Say 'Hello' if you can hear me.",
                generation_config=config
            )
            
            response_text = self._extract_response_text(test_response)
            return "hello" in response_text.lower()
            
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False

    # --- Helper and Parsing Methods (Unchanged but included for completeness) ---

    def _get_math_professor_prompt(self) -> str:
        """Get the system prompt for the math professor role."""
        return """
        You are an expert mathematics professor with years of teaching experience. 
        Your goal is to help students understand mathematical concepts by providing 
        clear, step-by-step solutions that are easy to follow.
        
        When solving problems:
        1. Break down complex problems into simple, logical steps
        2. Explain the reasoning behind each step
        3. Use clear mathematical notation
        4. Provide helpful insights and tips
        5. Connect the solution to broader mathematical concepts
        6. Ensure the final answer is clearly stated
        
        Always format your response with:
        - STEPS: A numbered list of solution steps
        - EXPLANATION: A detailed explanation of the approach
        - FINAL ANSWER: The clear final answer
        - DIFFICULTY: Assessment of problem difficulty (beginner/intermediate/advanced)
        """

    def _create_user_prompt(
        self,
        question: str,
        context: Optional[str] = None,
        source_material: Optional[str] = None
    ) -> str:
        """Create the user prompt with question and context."""
        prompt = f"Please solve this mathematical problem step by step:\n\nQuestion: {question}"
        if context:
            prompt += f"\n\nContext: {context}"
        if source_material:
            prompt += f"\n\nReference Material: {source_material}"
        prompt += "\n\nPlease provide a detailed step-by-step solution following the format specified above."
        return prompt

    def _extract_response_text(self, response: Any) -> str:
        """Safely extract text from Gemini response."""
        try:
            return response.text
        except Exception as e:
            logger.error(f"Could not extract text using response.text: {e}. Trying candidates.")
            try:
                return response.candidates[0].content.parts[0].text
            except Exception as e_inner:
                logger.error(f"Error extracting response text from candidates: {e_inner}")
                return "Error: Unable to extract response from Gemini API"

    def _parse_solution(self, solution_text: str) -> StepByStepSolution:
        """Parse the Gemini response into structured solution."""
        try:
            steps = self._extract_section(solution_text, "STEPS:", "EXPLANATION:")
            explanation = self._extract_section(solution_text, "EXPLANATION:", "FINAL ANSWER:")
            final_answer = self._extract_section(solution_text, "FINAL ANSWER:", "DIFFICULTY:")
            difficulty = self._extract_section(solution_text, "DIFFICULTY:", None)
            
            return StepByStepSolution(
                steps=self._parse_steps(steps),
                explanation=explanation.strip() or "Detailed explanation provided in steps.",
                final_answer=final_answer.strip() or "Answer provided in solution.",
                difficulty_assessment=self._validate_difficulty(difficulty.strip())
            )
        except Exception as e:
            logger.error(f"Error parsing Gemini solution: {str(e)}")
            return StepByStepSolution(
                steps=[solution_text],
                explanation="Could not parse the response from the AI.",
                final_answer="Please see the raw response in the steps.",
                difficulty_assessment="intermediate"
            )

    def _parse_steps(self, steps_text: str) -> List[str]:
        """Parse steps text into a clean list of steps."""
        if not steps_text.strip():
            return ["No steps provided in the solution."]
        
        # Split by newline and filter out empty lines
        return [line.strip() for line in steps_text.split('\n') if line.strip()]

    def _validate_difficulty(self, difficulty: str) -> str:
        """Validate and clean difficulty assessment."""
        difficulty_lower = difficulty.lower()
        for valid in ["beginner", "intermediate", "advanced"]:
            if valid in difficulty_lower:
                return valid
        return "intermediate"

    def _extract_section(self, text: str, start_marker: str, end_marker: Optional[str]) -> str:
        """Extract a section of text between markers."""
        try:
            start_idx = text.upper().find(start_marker.upper())
            if start_idx == -1: return ""
            
            start_idx += len(start_marker)
            
            end_idx = len(text)
            if end_marker:
                end_idx_find = text.upper().find(end_marker.upper(), start_idx)
                if end_idx_find != -1:
                    end_idx = end_idx_find
            
            return text[start_idx:end_idx].strip()
        except Exception as e:
            logger.error(f"Error extracting section: {str(e)}")
            return ""

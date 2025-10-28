import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep mathematical symbols
    text = re.sub(r'[^\w\s+\-*/=<>≤≥∑∫∏√∆∇∂()[\]{}.,!?]', '', text)
    
    return text

def extract_mathematical_terms(text: str) -> List[str]:
    """Extract mathematical terms from text."""
    math_patterns = [
        r'\b(?:derivative|integral|limit|equation|function|theorem)\b',
        r'\b(?:sin|cos|tan|log|ln|exp)\b',
        r'\b(?:matrix|vector|eigenvalue|determinant)\b',
        r'\b(?:probability|statistics|variance|mean)\b',
        r'[+\-*/=<>≤≥∑∫∏√∆∇∂]',
        r'\b\d+\.?\d*\b'
    ]
    
    terms = []
    for pattern in math_patterns:
        matches = re.findall(pattern, text.lower())
        terms.extend(matches)
    
    return list(set(terms))

def format_solution_steps(steps: List[str]) -> List[str]:
    """Format solution steps for consistent presentation."""
    formatted_steps = []
    
    for i, step in enumerate(steps, 1):
        if not step.strip():
            continue
            
        # Ensure step starts with number
        if not step.strip().startswith(str(i)):
            step = f"Step {i}: {step.strip()}"
        
        formatted_steps.append(step)
    
    return formatted_steps

def calculate_confidence_score(
    kb_score: Optional[float] = None,
    web_found: bool = False,
    source_count: int = 0
) -> float:
    """Calculate overall confidence score."""
    base_score = 0.5
    
    if kb_score:
        base_score = max(base_score, kb_score)
    
    if web_found:
        base_score += 0.1
    
    if source_count > 1:
        base_score += 0.1
    
    return min(base_score, 1.0)

def log_request(
    question: str,
    route_used: str,
    response_time: float,
    confidence: float
) -> Dict[str, Any]:
    """Log request details for analytics."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "question_length": len(question),
        "route_used": route_used,
        "response_time": response_time,
        "confidence_score": confidence,
        "mathematical_terms": extract_mathematical_terms(question)
    }

def validate_api_keys(openai_key: str, tavily_key: str) -> Dict[str, bool]:
    """Validate API key formats."""
    return {
        "openai_valid": openai_key.startswith("sk-") and len(openai_key) > 10,
        "tavily_valid": tavily_key.startswith("tvly-") and len(tavily_key) > 10
    }
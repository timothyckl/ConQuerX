"""
Input validation and sanitisation utilities.

Provides validation functions for LLM outputs and data processing.
"""

import re
from typing import List

from utils.logger import setup_logger

logger = setup_logger(__name__)


def sanitise_area_name(area: str) -> str:
    """
    Clean and validate area name.
    
    Converts underscores to spaces, lowercases, and validates format.
    
    Args:
        area: Raw area name from file
        
    Returns:
        Sanitised area name
        
    Raises:
        ValueError: If area name contains invalid characters
    """
    # remove underscores and convert to lowercase
    sanitised = area.replace("_", " ").lower().strip()
    
    # validate contains only letters, spaces, and common punctuation
    if not re.match(r'^[a-z\s\-&]+$', sanitised):
        raise ValueError(f"Invalid area name: {area}")
    
    return sanitised


def validate_questions(questions: List[str], min_count: int = 3) -> List[str]:
    """
    Validate question list from LLM response.
    
    Filters out empty/invalid questions and warns if count is low.
    
    Args:
        questions: List of question strings
        min_count: Minimum expected number of questions
        
    Returns:
        Filtered list of valid questions
    """
    # filter out empty or whitespace-only questions
    valid_questions = [q for q in questions if q and q.strip()]
    
    if len(valid_questions) < min_count:
        logger.warning(
            f"Fewer questions than expected: {len(valid_questions)} "
            f"(expected at least {min_count})"
        )
    
    return valid_questions


def validate_concepts(concepts: List[str]) -> List[str]:
    """
    Validate concept list from LLM response.
    
    Filters out empty concepts and validates format.
    
    Args:
        concepts: List of concept strings
        
    Returns:
        Filtered list of valid concepts
    """
    valid_concepts = []
    
    for concept in concepts:
        concept = concept.strip()
        if not concept:
            continue
            
        # concepts should be nouns/phrases, not full sentences
        if len(concept.split()) > 10:
            logger.warning(f"Concept seems too long, might be malformed: {concept[:50]}...")
            continue
            
        valid_concepts.append(concept)
    
    if not valid_concepts:
        logger.warning("No valid concepts extracted")
    
    return valid_concepts


def validate_quiz_format(quiz_text: str) -> bool:
    """
    Validate quiz has required format.
    
    Expected format:
        Quiz: <question>
        A. <option>
        B. <option>
        C. <option>
        D. <option>
    
    Args:
        quiz_text: Quiz text to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not quiz_text.startswith("Quiz:"):
        logger.warning("Quiz doesn't start with 'Quiz:'")
        return False
    
    # check for options A, B, C, D
    required_options = ['A.', 'B.', 'C.', 'D.']
    for option in required_options:
        if option not in quiz_text:
            logger.warning(f"Quiz missing option {option}")
            return False
    
    return True

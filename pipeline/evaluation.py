"""
Step 4: Quiz evaluation.

Evaluates generated quizzes on multiple dimensions: educational value,
diversity, area relevance, difficulty appropriateness, and comprehensiveness.
Uses an LLM to assign scores from 1-5 for each dimension.
"""

import json
import re
from typing import Dict, List, Any

from llama_index.core.llms import ChatMessage
from tqdm import tqdm

from config import LLM, LOG_FILE, MAX_RETRIES, RETRY_BASE_DELAY
from prompts import EVALUATION_PROMPT
from utils.logger import setup_logger
from utils.retry import retry_with_backoff

logger = setup_logger(__name__, log_file=LOG_FILE)

# evaluation dimensions used for scoring quizzes
EVALUATION_DIMENSIONS = [
    "Educational Value",
    "Diversity",
    "Area Relevance",
    "Difficulty Appropriateness",
    "Comprehensiveness",
]


def _create_score_dict(score: int) -> Dict[str, int]:
    """
    Create evaluation score dictionary with default values.
    
    Args:
        score: Default score to assign to all dimensions
        
    Returns:
        Dictionary mapping each evaluation dimension to the score
    """
    return {dim: score for dim in EVALUATION_DIMENSIONS}


def evaluate() -> None:
    """
    Evaluate generated quizzes using LLM-based assessment.
    
    For each quiz set:
    1. Retrieves corresponding Wikipedia summary
    2. Submits quiz to LLM for evaluation
    3. Extracts scores for 5 dimensions (1-5 scale each):
       - Educational Value
       - Diversity
       - Area Relevance
       - Difficulty Appropriateness
       - Comprehensiveness
    
    Uses retry logic with exponential backoff for robustness.
    Output is saved to wiki_evaluation.json.
    
    Raises:
        FileNotFoundError: If required input files don't exist
        IOError: If unable to write output file
    """
    # load Wikipedia summaries for evaluation context
    logger.info("Reading Wikipedia summaries from wiki.json")
    try:
        with open("wiki.json", "r") as f:
            wiki_information: Dict[str, Dict[str, Dict[str, List[str]]]] = json.loads(f.read())
    except FileNotFoundError:
        logger.error("wiki.json not found. Run quiz generation first (python main.py --step quiz)")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in wiki.json: {e}")
        raise

    # load quiz data for evaluation
    logger.info("Reading quiz data from quiz_concept_wiki.json")
    try:
        with open("quiz_concept_wiki.json", "r") as f:
            quizzes: Dict[str, Dict[str, Any]] = json.loads(f.read())
    except FileNotFoundError:
        logger.error("quiz_concept_wiki.json not found. Run quiz generation first (python main.py --step quiz)")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in quiz_concept_wiki.json: {e}")
        raise

    for level, areas in quizzes.items():
        logger.info(f"Evaluating quizzes for {level} level")
        
        for area, area_data in tqdm(areas.items(), desc=f"{level}"):
            if "quiz" not in area_data:
                continue
                
            questions: List[str] = area_data["questions"]
            quiz_lists: List[List[str]] = area_data["quiz"]

            llm_evaluation_metrics: List[Dict[str, int]] = []

            for question, quiz_list, wiki in zip(
                questions, quiz_lists, wiki_information[level][area]["summary"]
            ):
                # skip if no quizzes were generated
                if not quiz_list:
                    evaluation_dict = _create_score_dict(0)
                    llm_evaluation_metrics.append(evaluation_dict)
                    continue

                # aggregate all quizzes for this question
                aggregated_quiz = "\n\n".join(
                    [f"{i+1}: {quiz}" for i, quiz in enumerate(quiz_list)]
                )

                prompt = EVALUATION_PROMPT.format(
                    area, level, question, wiki, aggregated_quiz
                )

                try:
                    def evaluate_quiz() -> Dict[str, int]:
                        """
                        Inner function for retry logic.
                        
                        Calls LLM to evaluate quiz and extracts scores.
                        Pattern matches: ```json\n{content}\n```
                        
                        Returns:
                            Dictionary with evaluation scores
                            
                        Raises:
                            ValueError: If no JSON found in response
                            json.JSONDecodeError: If JSON is malformed
                        """
                        response = LLM.chat(
                            messages=[ChatMessage(role="user", content=prompt)]
                        )
                        
                        response_content = response.message.content
                        
                        if not response_content:
                            raise ValueError("Empty response from LLM")
                        
                        # extract JSON block from markdown-formatted LLM response
                        # pattern matches: ```json\n{content}\n```
                        match = re.search(
                            r"```json\n(.*?)\n```", response_content, re.DOTALL
                        )
                        
                        if not match:
                            raise ValueError("No JSON found in response")
                        
                        json_data = match.group(1)
                        scores = json.loads(json_data)
                        
                        return {dim: scores[dim] for dim in EVALUATION_DIMENSIONS}
                    
                    evaluation_dict = retry_with_backoff(
                        evaluate_quiz,
                        max_retries=MAX_RETRIES,
                        base_delay=RETRY_BASE_DELAY
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to evaluate quiz after {MAX_RETRIES} attempts: {e}")
                    # assign error marker (-1) for all dimensions
                    evaluation_dict = _create_score_dict(-1)

                llm_evaluation_metrics.append(evaluation_dict)

            area_data["llm_score"] = llm_evaluation_metrics

    logger.info(f"Writing evaluation results to wiki_evaluation.json")
    with open("wiki_evaluation.json", "w") as f:
        f.write(json.dumps(quizzes, indent=4))
    
    logger.info("Evaluation completed successfully")

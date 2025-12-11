"""
Step 1: Seed question generation.

Generates initial questions for each subject area at different education levels
using an LLM. Questions are designed to be diverse and appropriate for the
specified education level.
"""

import json
from typing import Dict, List

from llama_index.core.llms import ChatMessage
from prompts import SEED_QUESTION_GENERATION_PROMPT
from tqdm import tqdm
from config import LLM, EDUCATION_LEVELS, LOG_FILE
from utils.logger import setup_logger
from utils.validation import sanitise_area_name, validate_questions

logger = setup_logger(__name__, log_file=LOG_FILE)


def seed_questions() -> None:
    """
    Generate seed questions for different education levels and subject areas.
    
    Reads subject areas from areas.txt and uses an LLM to generate 5 diverse
    questions for each area at primary school, high school, and PhD levels.
    Output is saved to questions.json.
    
    Raises:
        FileNotFoundError: If areas.txt doesn't exist
        IOError: If unable to write questions.json
    """
    logger.info("Reading subject areas from areas.txt")
    with open("areas.txt", "r") as f:
        areas: List[str] = f.read().splitlines()

    out: Dict[str, Dict[str, List[str]]] = {}

    for level in EDUCATION_LEVELS:
        out[level] = {}
        logger.info(f"Generating questions for {level} level")

        for area in tqdm(areas, desc=f"{level}"):
            area = sanitise_area_name(area)
            prompt = SEED_QUESTION_GENERATION_PROMPT.format(area, level)

            response = LLM.chat(
                messages=[
                    ChatMessage(role="user", content=prompt),
                ]
            )

            questions = response.message.content.split("\n")
            questions = [q.strip() for q in questions if q.strip()]
            questions = validate_questions(questions, min_count=3)
            out[level][area] = questions

    logger.info("Writing questions to questions.json")
    with open("questions.json", "w") as f:
        f.write(json.dumps(out, indent=4))
    
    logger.info(f"Successfully generated questions for {len(areas)} areas across {len(EDUCATION_LEVELS)} levels")

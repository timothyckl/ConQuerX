"""
Step 2: Concept extraction.

Extracts key concepts from each generated question using an LLM.
Concepts are nouns representing topics relevant to the question.
"""

import json
from typing import Dict, List

from config import LLM, LOG_FILE
from llama_index.core.llms import ChatMessage
from prompts import CONCEPT_GENERATION_PROMPT
from tqdm import tqdm
from utils.logger import setup_logger
from utils.validation import validate_concepts

logger = setup_logger(__name__, log_file=LOG_FILE)


def extract_concepts() -> None:
    """
    Extract key concepts from generated questions.
    
    Reads questions from questions.json and uses an LLM to identify key concepts
    for each question. Concepts are nouns or noun phrases relevant to the question's
    subject matter. Output is saved to concepts.json.
    
    Raises:
        FileNotFoundError: If questions.json doesn't exist
        IOError: If unable to write concepts.json
    """
    logger.info("Reading questions from questions.json")
    with open("questions.json", "r") as f:
        questions: Dict[str, Dict[str, List[str]]] = json.loads(f.read())

    for level, areas in questions.items():
        logger.info(f"Extracting concepts for {level} level")
        
        for area, question_list in tqdm(areas.items(), desc=f"{level}"):
            # create new structure for area data
            areas[area] = {
                "questions": question_list,
                "concepts": []
            }

            for question in question_list:
                prompt = CONCEPT_GENERATION_PROMPT.format(question, level, area)

                response = LLM.chat(
                    messages=[
                        ChatMessage(role="user", content=prompt),
                    ]
                )

                # parse concept list from LLM response
                answer = response.message.content.strip("[]").split(", ")
                concepts = [i.strip() for i in answer if i.strip()]
                concepts = validate_concepts(concepts)
                areas[area]["concepts"].append(concepts)

    logger.info("Writing concepts to concepts.json")
    with open("concepts.json", "w") as f:
        f.write(json.dumps(questions, indent=4))
    
    logger.info("Concept extraction completed successfully")

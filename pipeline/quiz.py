"""
Step 3: Quiz generation.

Generates educational quizzes based on Wikipedia content related to
extracted concepts. Each quiz contains a question and four options,
with the correct answer always in position A.
"""

import json
import os
import time
from typing import Any, Dict, List

from llama_index.core import Settings, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.llms import ChatMessage
from llama_index.core.schema import Document
from tqdm import tqdm
from wikipediaapi import Wikipedia

from config import (CACHE_DIR, CHUNK_OVERLAP, CHUNK_SIZE, EMBED_MODEL, INDEX_DIR, LLM,
                    LOG_FILE, RETRIEVAL_TOP_K, WIKIPEDIA_DELAY,
                    WIKIPEDIA_USER_AGENT)
from prompts import QUESTION_GENERATION_PROMPT, SUMMARY_GENERATION_PROMPT
from utils.cache import WikipediaCache
from utils.logger import setup_logger
from utils.validation import validate_quiz_format

logger = setup_logger(__name__, log_file=LOG_FILE)


def generate_quiz() -> None:
    """
    Generate educational quizzes based on Wikipedia content.

    For each question and its associated concepts:
    1. Fetches Wikipedia pages for the concepts
    2. Creates a semantic index for information retrieval
    3. Retrieves relevant content chunks for the question
    4. Generates a summary from retrieved content
    5. Creates 3 quiz questions based on the summary

    Output files:
    - quiz_concept_wiki.json: Questions, concepts, and generated quizzes
    - wiki.json: Wikipedia summaries and raw content

    Raises:
        FileNotFoundError: If concepts.json doesn't exist
        IOError: If unable to write output files
    """
    logger.info("Initializing Wikipedia API client")
    wiki_obj: object = Wikipedia(WIKIPEDIA_USER_AGENT, "en")
    wiki_cache = WikipediaCache(cache_dir=CACHE_DIR)

    logger.info("Reading concepts from concepts.json")
    with open("concepts.json", "r") as f:
        data: Dict[str, Dict[str, Any]] = json.loads(f.read())

    # configure llama-index settings for vector indexing
    Settings.llm = LLM
    Settings.embed_model = EMBED_MODEL
    Settings.chunk_size = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP

    wiki: Dict[str, Dict[str, Dict[str, List[str]]]] = {}

    for level, areas in data.items():
        wiki[level] = {}
        logger.info(f"Generating quizzes for {level} level")

        for area, question_data in tqdm(areas.items(), desc=f"{level}"):
            wiki[level][area] = {"summary": [], "wiki": []}
            data[level][area]["quiz"] = []

            for question, concepts in zip(
                question_data["questions"], question_data["concepts"]
            ):
                wiki_docs: List[Document] = []

                # fetch Wikipedia pages for each concept (with caching)
                for concept in concepts:
                    # try cache first
                    cached_content = wiki_cache.get(concept)

                    if cached_content:
                        # use cached content
                        doc = Document(text=cached_content)
                        wiki_docs.append(doc)
                        logger.debug(f"Using cached Wikipedia page: {concept}")
                    else:
                        # fetch from API with rate limiting
                        try:
                            logger.debug(f"Fetching Wikipedia page: {concept}")
                            time.sleep(WIKIPEDIA_DELAY)  # rate limiting

                            page_py = wiki_obj.page(concept)
                            page_content = page_py.text
                            page_id = str(page_py.pageid)

                            # cache for future use
                            wiki_cache.set(concept, page_content, page_id)

                            doc = Document(id_=page_id, text=page_content)
                            wiki_docs.append(doc)
                        except Exception as e:
                            logger.warning(
                                f"Could not load Wikipedia page for '{concept}': {e}"
                            )
                            continue

                if os.path.exists(INDEX_DIR):
                    storage = StorageContext.from_defaults(persist_dir=INDEX_DIR)
                    index = load_index_from_storage(storage_context=storage) 
                else: 
                    index = VectorStoreIndex.from_documents(wiki_docs)
                    index.storage_context.persist(persist_dir=INDEX_DIR)

                retriever = index.as_retriever(similarity_top_k=RETRIEVAL_TOP_K)
                nodes = retriever.retrieve(question)

                # concatenate retrieved content chunks
                wiki_information = ""
                for i, node in enumerate(nodes):
                    wiki_information += f"\n\nInformation {i+1}:\n"
                    wiki_information += node.node.get_content()

                wiki_information = wiki_information.strip()

                # generate summary from Wikipedia content
                prompt = SUMMARY_GENERATION_PROMPT.format(
                    area, level, wiki_information, question
                )

                response = LLM.chat(
                    messages=[
                        ChatMessage(role="user", content=prompt),
                    ]
                )

                summary = response.message.content

                # generate quiz questions based on summary
                prompt = QUESTION_GENERATION_PROMPT.format(
                    area, level, level, summary, question
                )

                response = LLM.chat(
                    messages=[
                        ChatMessage(role="user", content=prompt),
                    ]
                )

                # parse quiz sections from LLM response
                content = response.message.content
                quiz: List[str] = []
                for section in content.split("[Quiz]"):
                    section = section.strip()
                    if section and section.startswith("Quiz"):
                        if validate_quiz_format(section):
                            quiz.append(section)
                        else:
                            logger.warning("Invalid quiz format, skipping")

                data[level][area]["quiz"].append(quiz)
                wiki[level][area]["summary"].append(summary)
                wiki[level][area]["wiki"].append(wiki_information)

    logger.info("Writing quizzes to quiz_concept_wiki.json")
    with open("quiz_concept_wiki.json", "w") as f:
        f.write(json.dumps(data, indent=4))

    logger.info("Writing Wikipedia content to wiki.json")
    with open("wiki.json", "w") as f:
        f.write(json.dumps(wiki, indent=4))

    logger.info("Quiz generation completed successfully")

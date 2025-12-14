"""
Configuration module for ConQuerX pipeline.

Contains all configurable parameters, file paths, and initialized
LLM/embedding models. Settings can be overridden via environment variables.
"""

import os

from dotenv import load_dotenv
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

# load environment variables from .env file
load_dotenv()

# ============================================================================
# Environment Variables (with defaults)
# ============================================================================

WIKIPEDIA_USER_AGENT = os.getenv("WIKIPEDIA_USER_AGENT", "ConQuerX-Research/1.0")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embeddinggemma")

# ============================================================================
# File Paths
# ============================================================================

AREAS_FILE = "areas.txt"
QUESTIONS_FILE = "questions.json"
CONCEPTS_FILE = "concepts.json"
QUIZ_FILE = "quiz_concept_wiki.json"
WIKI_FILE = "wiki.json"
EVALUATION_FILE = "wiki_evaluation.json"
LOG_FILE = "pipeline.log"
CACHE_DIR = ".cache/wikipedia"
INDEX_DIR = ".indices"

# ============================================================================
# LLM Settings
# ============================================================================

RETRIEVAL_TOP_K = 5
CHUNK_SIZE = 128
CHUNK_OVERLAP = 50

# ============================================================================
# Education Levels
# ============================================================================

EDUCATION_LEVELS = ["primary school", "high school", "college"]

# ============================================================================
# Retry Settings
# ============================================================================

MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0

# ============================================================================
# Rate Limiting
# ============================================================================

WIKIPEDIA_DELAY = 0.1  # seconds between API calls

# ============================================================================
# Initialized Objects
# ============================================================================

LLM = Ollama(
    model=OLLAMA_MODEL,
    request_timeout=120.0,
    json_mode=True,
)
EMBED_MODEL = OllamaEmbedding(model_name=EMBEDDING_MODEL)

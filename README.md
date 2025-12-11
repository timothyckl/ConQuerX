# ConQuerX

[![arXiv](https://img.shields.io/badge/arXiv-2503.14662-b31b1b.svg)](https://arxiv.org/abs/2503.14662)

> A refactored implementation of the ConQuer framework [Fu et al., 2025] for concept-based quiz generation. This version provides improved code organisation, caching, and modular architecture to serve as a foundation for research experiments.

## Overview

ConQuerX is a research project that automatically generates educational quizzes using large language models (LLMs) and Wikipedia as an external knowledge source. The system implements a four-stage pipeline that creates domain-specific questions, extracts relevant concepts, retrieves contextual information, and generates multiple-choice quizzes tailored to different education levels.

This implementation is based on the ConQuer framework ([Fu et al., 2025](https://arxiv.org/abs/2503.14662)), with planned extensions (hence the "X") to explore alternative indexing strategies, retrieval methods, and question generation approaches. The current implementation uses Ollama for local LLM inference and LlamaIndex for retrieval-augmented generation (RAG).

## Motivation

Educational quizzes play a crucial role in reinforcing students' understanding of key concepts and encouraging self-directed learning. However, creating high-quality quizzes requires deep domain expertise and significant time investment from educators.

Whilst LLMs have dramatically improved the efficiency of quiz generation, concerns remain about the quality and accuracy of AI-generated educational content. Without grounding in reliable external knowledge sources, LLMs may hallucinate incorrect information or generate questions that don't require meaningful domain expertise.

The ConQuer framework (Fu et al., 2025) addresses these challenges through:

- **Grounding generation in Wikipedia**: Ensures factual accuracy and verifiability
- **Using concept-based retrieval**: Focuses on relevant domain knowledge rather than generic information
- **Systematic evaluation**: Assesses quiz quality across multiple dimensions (educational value, diversity, relevance, difficulty, comprehensiveness)
- **Supporting reproducible research**: Provides a framework for comparing different approaches to automated quiz generation

This implementation maintains the original framework's approach whilst providing a cleaner, more maintainable codebase for research experimentation.

## About This Implementation

This repository provides a refactored version of the original ConQuer codebase. The core methodology remains unchanged and this implementation focuses on code quality and research infrastructure.

**Code organisation**: The pipeline is restructured into modular stages with clear separation of concerns. Utility modules handle common operations (logging, caching, retry logic, validation), making the codebase easier to understand and extend.

**Developer experience**: Wikipedia responses are cached locally to reduce API calls during development. The command-line interface supports running individual pipeline stages, configurable logging verbosity, and cache management.

**Configuration**: Environment variables (via `.env`) and centralised settings (`config.py`) make it straightforward to swap models, adjust RAG parameters, and customise education levels.

**Research infrastructure**: The clean architecture facilitates experimentation with alternative approaches. See [RESEARCH.md](RESEARCH.md) for planned research directions, including different retrieval strategies, question formats, and evaluation methods.

## System Architecture

### Pipeline Overview

```
Input: areas.txt
  │
  ▼
┌──────────────────────┐
│   1. SEEDING         │  Generate seed questions using LLM
│   questions.json     │  • 5 questions per area/level
└──────────────────────┘  • Requires domain expertise
  │
  ▼
┌──────────────────────┐
│   2. CONCEPTS        │  Extract key concepts from questions
│   concepts.json      │  • Nouns representing topics
└──────────────────────┘  • Linked to seed questions
  │
  ▼
┌──────────────────────┐       ┌─────────────────────┐
│   3. QUIZ GEN (RAG)  │◄──────│  Wikipedia API      │
│   quiz_*.json        │       │  + Caching          │
│   wiki.json          │       └─────────────────────┘
└──────────────────────┘
  │  • Fetch Wikipedia pages
  │  • Semantic indexing (embeddings)
  │  • Retrieve relevant chunks
  │  • Generate summary + 3 quizzes
  │
  ▼
┌──────────────────────┐
│   4. EVALUATION      │  Assess quiz quality (LLM-as-judge)
│   *_evaluation.json  │  • 5 dimensions (1-5 scale each)
└──────────────────────┘  • Educational value, diversity, etc.
```

### Technical Approach

The framework uses **Retrieval-Augmented Generation (RAG)** to ground quiz generation in verifiable Wikipedia content:

1. **Concept Extraction**: An LLM identifies key concepts (nouns/topics) from each seed question
2. **Document Retrieval**: Wikipedia pages for each concept are fetched and cached locally
3. **Semantic Indexing**: Documents are chunked and embedded using `embeddinggemma` to create a vector index
4. **Context Retrieval**: Given a question, the top-K most relevant chunks are retrieved via semantic similarity
5. **Summary Generation**: Retrieved chunks are synthesised into a coherent summary
6. **Quiz Creation**: The LLM generates 3 multiple-choice questions based on the summary
7. **Quality Assessment**: Another LLM evaluates the generated quizzes across 5 dimensions

This approach ensures quizzes are grounded in factual content whilst maintaining the flexibility and naturalness of LLM-generated text.

## Installation

### Prerequisites

- **Python 3.8+** - Core runtime
- **[Ollama](https://ollama.ai/)** - Local LLM inference engine
- **Required Ollama models**:
  - `gemma3:4b` - Main LLM for generation and evaluation
  - `embeddinggemma` - Text embeddings for semantic search

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ConQuerX.git
   cd ConQuerX
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your Wikipedia user agent (required by Wikipedia API):

   ```bash
   WIKIPEDIA_USER_AGENT=your-email@example.com
   ```

4. **Pull Ollama models**

   ```bash
   ollama pull gemma3:4b
   ollama pull embeddinggemma
   ```

   Verify models are available:

   ```bash
   ollama list
   ```

5. **Optional: Customise subject areas**

   Edit `areas.txt` to add/remove subject areas for quiz generation.

## Usage

### Quick Start

Run the complete pipeline (all four stages):

```bash
python main.py
```

This will:

1. Generate seed questions for all areas in `areas.txt`
2. Extract concepts from questions
3. Fetch Wikipedia content and generate quizzes
4. Evaluate quiz quality

### Running Specific Pipeline Steps

Run individual stages for iterative development:

```bash
# Generate seed questions only
python main.py --step seed

# Extract concepts only
python main.py --step concepts

# Generate quizzes only (requires concepts.json)
python main.py --step quiz

# Evaluate quizzes only (requires quiz_*.json)
python main.py --step eval
```

### Command-Line Options

| Option           | Description                                                                         | Example         |
| ---------------- | ----------------------------------------------------------------------------------- | --------------- |
| `--step <stage>` | Run specific pipeline stage: `seed`, `concepts`, `quiz`, `eval`, or `all` (default) | `--step quiz`   |
| `--verbose`      | Enable DEBUG-level logging for detailed output                                      | `--verbose`     |
| `--clear-cache`  | Clear Wikipedia cache before running                                                | `--clear-cache` |

### Common Workflows

**Development iteration**:

```bash
# Clear cache and run quiz generation with verbose logging
python main.py --step quiz --verbose --clear-cache
```

**Debugging a specific stage**:

```bash
# Run evaluation with detailed logs
python main.py --step eval --verbose
```

**Full pipeline with clean slate**:

```bash
# Clear all cached data and regenerate everything
python main.py --clear-cache --verbose
```

## Pipeline Details

### 1. Seeding Questions

**Purpose**: Generate initial domain-specific questions that require expertise to answer.

**Input**: `areas.txt` (list of subject areas)

**Output**: `questions.json` (5 questions per area per education level)

**Process**:

- For each subject area and education level:
  - Prompts LLM to generate 5 diverse questions appropriate for that level
  - Questions designed to require domain knowledge (not easily answered by LLMs alone)
  - Validates minimum question count before proceeding

**Example Generated Question**:

```json
{
  "area": "Accounting",
  "level": "College",
  "question": "How do different accounting standards (e.g., GAAP vs. IFRS) impact the valuation of intangible assets like brand recognition or customer relationships, and what are the key arguments for each approach?"
}
```

### 2. Extracting Concepts

**Purpose**: Identify key concepts (nouns/topics) relevant to each question.

**Input**: `questions.json`

**Output**: `concepts.json` (list of concepts per question)

**Process**:

- For each question:
  - Prompts LLM to extract key concepts as nouns/noun phrases
  - Concepts represent topics that could be looked up in Wikipedia
  - Validates extracted concepts before storing

**Example Extracted Concepts**:

```json
{
  "question": "How do different accounting standards (e.g., GAAP vs. IFRS)...",
  "concepts": [
    "accounting standards",
    "GAAP",
    "IFRS",
    "intangible assets",
    "brand recognition",
    "customer relationships",
    "valuation",
    "arguments"
  ]
}
```

### 3. Generating Quizzes (RAG)

**Purpose**: Create 3 multiple-choice quizzes per question using Wikipedia content.

**Input**: `concepts.json`

**Output**:

- `quiz_concept_wiki.json` (generated quizzes)
- `wiki.json` (Wikipedia summaries and raw content)

**Process**:

1. **Fetch Wikipedia pages** for each concept (with local caching)
2. **Create semantic index** using embeddings (`embeddinggemma`)
3. **Retrieve relevant chunks** (top-K most similar to the question)
4. **Generate summary** from retrieved content
5. **Create 3 quizzes** based on the summary

**RAG Configuration** (in `config.py`):

- `CHUNK_SIZE = 128` - Characters per chunk
- `CHUNK_OVERLAP = 50` - Overlap between chunks
- `RETRIEVAL_TOP_K = 5` - Number of chunks to retrieve

**Example Generated Quiz**:

```
[Quiz]
Quiz: Which of the following best describes a key difference in how U.S. GAAP
and IFRS typically treat inventory valuation, influencing intangible asset
valuation?

A. GAAP generally permits the use of LIFO (Last-In, First-Out), while IFRS
   primarily utilises FIFO (First-In, First-Out).
B. IFRS consistently favours the weighted average method for inventory
   valuation, unlike GAAP which requires perpetual inventory systems.
C. Both GAAP and IFRS utilise the same inventory valuation methods,
   prioritising cost of goods sold accuracy.
D. IFRS mandates the use of the specific retail method for inventory
   valuation, offering greater transparency than GAAP.
```

**Note**: By design (following the original ConQuer framework), the correct answer is always **option A**.

### 4. Evaluating Quizzes

**Purpose**: Assess quiz quality using LLM-as-judge methodology.

**Input**:

- `quiz_concept_wiki.json`
- `wiki.json`

**Output**: `wiki_evaluation.json` (scores for each quiz set)

**Process**:

- For each quiz set:
  - Provides quiz + Wikipedia summary to LLM
  - Extracts structured scores (1-5) for 5 dimensions
  - Uses retry logic with exponential backoff for robustness

**Evaluation Dimensions** (1-5 scale):

1. **Educational Value**: Do students learn from these quizzes?
   - 1 = Not educational at all
   - 5 = Highly educational, great learning value

2. **Diversity**: Do quizzes cover a broad range of topics?
   - 1 = Very repetitive, narrow focus
   - 5 = Extremely diverse, broad coverage

3. **Area Relevance**: Are quizzes relevant to the question and subject area?
   - 1 = Not relevant at all
   - 5 = Perfectly relevant, directly tied to question

4. **Difficulty Appropriateness**: Do quizzes match the education level?
   - 1 = Too easy or too difficult
   - 5 = Perfectly suited to student's level

5. **Comprehensiveness**: Do quizzes cover depth and breadth of the topic?
   - 1 = Very superficial
   - 5 = Highly comprehensive with great depth

**Example Evaluation Output**:

```json
{
  "Educational Value": 4,
  "Diversity": 3,
  "Area Relevance": 5,
  "Difficulty Appropriateness": 4,
  "Comprehensiveness": 3
}
```

## Output Files

All output files are generated in the project root directory:

| File                     | Description                                   | Size (typical) |
| ------------------------ | --------------------------------------------- | -------------- |
| `questions.json`         | Generated seed questions by level and area    | ~40KB          |
| `concepts.json`          | Extracted concepts for each question          | ~95KB          |
| `quiz_concept_wiki.json` | Generated quizzes with questions and concepts | ~300KB         |
| `wiki.json`              | Wikipedia summaries and raw content           | ~650KB         |
| `wiki_evaluation.json`   | Quiz evaluation scores (5 dimensions)         | ~315KB         |
| `pipeline.log`           | Detailed execution logs with timestamps       | Varies         |

**Note**: Output files are excluded from version control (see `.gitignore`) as they're regenerated by the pipeline.

## Configuration

### Environment Variables (`.env`)

```bash
# Required: Your email for Wikipedia API user agent
WIKIPEDIA_USER_AGENT=your-email@example.com

# Optional: Override default Ollama models
OLLAMA_MODEL=gemma3:4b
EMBEDDING_MODEL=embeddinggemma
```

### Pipeline Settings (`config.py`)

**LLM Configuration**:

- `OLLAMA_MODEL` - Main LLM for generation/evaluation (default: `gemma3:4b`)
- `EMBEDDING_MODEL` - Embedding model for semantic search (default: `embeddinggemma`)

**RAG Parameters**:

- `CHUNK_SIZE` - Characters per chunk for indexing (default: `128`)
- `CHUNK_OVERLAP` - Overlap between chunks (default: `50`)
- `RETRIEVAL_TOP_K` - Number of chunks to retrieve (default: `5`)

**Retry Configuration**:

- `MAX_RETRIES` - Maximum retry attempts for failed operations (default: `3`)
- `RETRY_BASE_DELAY` - Initial delay for exponential backoff (default: `1.0` seconds)

**Rate Limiting**:

- `WIKIPEDIA_DELAY` - Delay between Wikipedia API calls (default: `0.1` seconds)

**Education Levels**:

```python
# Current implementation (modify in config.py)
EDUCATION_LEVELS = ["primary school", "high school", "college"]

# Original options
# EDUCATION_LEVELS = ["primary school", "high school", "PhD"]
```

**File Paths**:

- Customise input/output file names in `config.py`
- Change cache directory location via `CACHE_DIR`

## Evaluation Framework

The framework uses an **LLM-as-judge** methodology to systematically assess quiz quality. This approach:

1. **Standardises evaluation**: Uses structured prompts to ensure consistent scoring
2. **Scales efficiently**: Evaluates hundreds of quizzes without human annotation
3. **Captures multiple dimensions**: Goes beyond simple correctness to assess educational value
4. **Provides detailed feedback**: Generates reasoning before assigning scores

### Evaluation Process

For each quiz set:

1. LLM receives the quiz, original question, and Wikipedia summary
2. LLM generates step-by-step reasoning about quiz quality
3. LLM assigns scores (1-5) for each of the 5 dimensions
4. Scores are extracted from structured JSON response
5. If extraction fails, retry with exponential backoff (up to 3 attempts)

## Project Structure

```bash
ConQuerX/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .env                   # Your environment configuration (not tracked)
├── .gitignore             # Git ignore rules
│
├── config.py              # Configuration and constants
├── main.py                # CLI entry point
├── prompts.py             # LLM prompt templates
├── areas.txt              # Subject areas for quiz generation
│
├── pipeline/              # Pipeline stage implementations
│   ├── __init__.py
│   ├── seeding.py         # Stage 1: Question generation
│   ├── concepts.py        # Stage 2: Concept extraction
│   ├── quiz.py            # Stage 3: Quiz generation (RAG)
│   └── evaluation.py      # Stage 4: Quiz evaluation
│
└── utils/                 # Utility modules
    ├── __init__.py
    ├── logger.py          # Logging configuration
    ├── validation.py      # Input validation functions
    ├── retry.py           # Retry logic with backoff
    └── cache.py           # Wikipedia caching system
```

**Generated files**:

```bash
├── questions.json         # Generated seed questions
├── concepts.json          # Extracted concepts
├── quiz_concept_wiki.json # Generated quizzes
├── wiki.json              # Wikipedia content
├── wiki_evaluation.json   # Evaluation scores
├── pipeline.log           # Execution logs
└── .cache/                # Wikipedia page cache
```

## Acknowledgements

This repository provides a refactored implementation of the ConQuer framework introduced in:

**ConQuer: A Framework for Concept-Based Quiz Generation**  
Yicheng Fu, Zikui Wang, Liuxin Yang, Meiqing Huo, Zhongdongming Dai  
_arXiv preprint arXiv:2503.14662_, 2025  
[[Paper]](https://arxiv.org/abs/2503.14662) [[Original Code]](https://github.com/sofyc/ConQuer)

We thank the original authors for their excellent work and for open-sourcing their code, which this implementation builds upon.

### Citation

If you use this implementation in your research, please cite the original ConQuer paper. If you specifically use the code improvements or experimental extensions from this repository, you may additionally cite this implementation:

```bibtex
@article{fu2025conquer,
  title={ConQuer: A Framework for Concept-Based Quiz Generation},
  author={Fu, Yicheng and Wang, Zikui and Yang, Liuxin and Huo, Meiqing and Dai, Zhongdongming},
  journal={arXiv preprint arXiv:2503.14662},
  year={2025}
}

@software{conquerx2025,
  title={ConQuerX: Extended Framework for Concept-Based Quiz Generation},
  author={Timothy Chia Kai Lun},
  year={2025},
  url={https://github.com/timothyckl/ConQuerX}
}
```

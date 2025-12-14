from llama_index.core.extractors import KeywordExtractor, SummaryExtractor

from prompts import CONCEPT_GENERATION_PROMPT, SUMMARY_GENERATION_PROMPT

concept_extractor = KeywordExtractor(
    prompt_template=CONCEPT_GENERATION_PROMPT,
    keywords=5,
)

summary_extractor = SummaryExtractor(
    prompt_template=SUMMARY_GENERATION_PROMPT,
    summaries=["self"],
)

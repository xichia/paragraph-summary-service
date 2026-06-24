from __future__ import annotations

import re

from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.models.domain import (
    ProviderBatchResult,
    ProviderParagraphRequest,
    ProviderParagraphResult,
)
from paragraph_summary_service.prompts.templates import PromptTemplate
from paragraph_summary_service.usage.costs import estimate_cost
from paragraph_summary_service.usage.tokens import estimate_tokens

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class MockProvider:
    name = "mock"
    default_model = "mock-deterministic-v1"

    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_paragraph_summaries(
        self,
        *,
        records: list[ProviderParagraphRequest],
        template: PromptTemplate,
        model: str,
    ) -> ProviderBatchResult:
        results: list[ProviderParagraphResult] = []
        input_tokens = 0
        output_tokens = 0
        for record in records:
            summary = deterministic_sentence_summary(record.text, record.max_summary_tokens)
            results.append(ProviderParagraphResult(record_id=record.record_id, summary=summary))
            input_tokens += estimate_tokens(record.text, self.settings.token_chars_per_token)
            output_tokens += estimate_tokens(summary, self.settings.token_chars_per_token)
        return ProviderBatchResult(
            results=results,
            usage=estimate_cost(self.name, model, input_tokens, output_tokens),
        )


def deterministic_sentence_summary(text: str, max_tokens: int = 48) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "The paragraph is empty."
    first = _SENTENCE_RE.split(cleaned)[0].strip()
    words = first.split()
    max_words = max(6, max_tokens)
    if len(words) > max_words:
        first = " ".join(words[:max_words]).rstrip(",;:") + "."
    if first[-1] not in ".!?":
        first += "."
    return first

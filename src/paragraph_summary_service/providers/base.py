from __future__ import annotations

from typing import Protocol

from paragraph_summary_service.models.domain import ProviderBatchResult, ProviderParagraphRequest
from paragraph_summary_service.prompts.templates import PromptTemplate


class ProviderError(RuntimeError):
    error_code = "PROVIDER_ERROR"


class ProviderNotEnabledError(ProviderError):
    error_code = "PROVIDER_NOT_ENABLED"


class ProviderResponseError(ProviderError):
    error_code = "PROVIDER_RESPONSE_ERROR"


class ParagraphSummaryProvider(Protocol):
    name: str
    default_model: str

    def generate_paragraph_summaries(
        self,
        *,
        records: list[ProviderParagraphRequest],
        template: PromptTemplate,
        model: str,
    ) -> ProviderBatchResult:
        ...

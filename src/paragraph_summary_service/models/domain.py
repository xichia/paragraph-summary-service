from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def plus(self, other: "Usage") -> "Usage":
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            estimated_cost_usd=round(self.estimated_cost_usd + other.estimated_cost_usd, 8),
        )


@dataclass(frozen=True)
class ParagraphRecord:
    document_id: str
    record_id: str
    source_ref: str
    text: str
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    provenance: str = "deepreader"


@dataclass(frozen=True)
class ParagraphSummary:
    document_id: str
    record_id: str
    source_ref: str
    input_text_hash: str
    summary: str
    summary_style: str
    template_version: str
    provider: str
    model: str
    cache_hit: bool
    status: str
    usage: Usage
    metadata: dict[str, Any] = field(default_factory=dict)
    provenance: str = "deepreader"
    error_code: str | None = None


@dataclass(frozen=True)
class ProviderParagraphRequest:
    record_id: str
    source_ref: str
    text: str
    input_text_hash: str
    max_summary_tokens: int


@dataclass(frozen=True)
class ProviderParagraphResult:
    record_id: str
    summary: str
    status: str = "completed"
    error_code: str | None = None


@dataclass(frozen=True)
class ProviderBatchResult:
    results: list[ProviderParagraphResult]
    usage: Usage
    raw_provider_metadata: dict[str, Any] = field(default_factory=dict)

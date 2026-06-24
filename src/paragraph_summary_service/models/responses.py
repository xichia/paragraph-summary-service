from typing import Any

from pydantic import BaseModel, ConfigDict


class UsageResponse(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class ParagraphSummaryArtifactResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    document_id: str
    output_path: str
    records_received: int
    records_completed: int
    records_failed: int
    cache_hits: int
    provider: str
    model: str
    template_version: str
    usage: UsageResponse
    batches_processed: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    provider_default: str
    external_provider_calls_enabled: bool

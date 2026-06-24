from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ParagraphRecordInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str = Field(min_length=1, max_length=512)
    source_ref: str = Field(default="", max_length=1024)
    text: str = Field(min_length=1)
    checksum: str | None = Field(default=None, max_length=256)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: str = Field(default="deepreader", max_length=128)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class ParagraphSummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1, max_length=256)
    records: list[ParagraphRecordInput] = Field(min_length=1)
    provider: str = Field(default="mock", max_length=64)
    model: str | None = Field(default=None, max_length=128)
    template_version: str = Field(default="paragraph_sentence_batch_v1", max_length=128)
    max_summary_tokens_per_record: int = Field(default=48, ge=8, le=160)
    output_format: Literal["jsonl"] = "jsonl"

    @model_validator(mode="after")
    def record_ids_must_be_unique(self) -> "ParagraphSummaryRequest":
        ids = [record.record_id for record in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("record_id values must be unique within a request")
        return self

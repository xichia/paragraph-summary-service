from __future__ import annotations

from dataclasses import dataclass

from paragraph_summary_service.artifacts.ids import make_artifact_id
from paragraph_summary_service.artifacts.writer import write_jsonl_artifact
from paragraph_summary_service.batching.minute_packer import TokenBudgetPacker
from paragraph_summary_service.cache.keys import build_cache_key, sha256_text
from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.models.domain import (
    ParagraphRecord,
    ParagraphSummary,
    ProviderParagraphRequest,
    Usage,
)
from paragraph_summary_service.models.requests import ParagraphSummaryRequest
from paragraph_summary_service.models.responses import (
    ParagraphSummaryArtifactResponse,
    UsageResponse,
)
from paragraph_summary_service.observability.structured_logger import get_logger, log_event
from paragraph_summary_service.prompts.templates import get_template
from paragraph_summary_service.providers.base import ProviderError
from paragraph_summary_service.providers.registry import get_provider, resolve_model
from paragraph_summary_service.safety.limits import validate_paragraph_request_limits
from paragraph_summary_service.safety.redaction import redact_metadata, redact_text
from paragraph_summary_service.storage.repositories import SummaryRepository

SUMMARY_STYLE = "paragraph_sentence"


@dataclass(frozen=True)
class SummaryPipelineResult:
    response: ParagraphSummaryArtifactResponse
    artifact_path: str


class ParagraphSummaryService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.repository = SummaryRepository(settings.summary_db_path)
        self.logger = get_logger()

    def summarise_request(self, request: ParagraphSummaryRequest) -> SummaryPipelineResult:
        validate_paragraph_request_limits(request, self.settings)
        records = [
            ParagraphRecord(
                document_id=request.document_id,
                record_id=item.record_id,
                source_ref=item.source_ref or item.record_id,
                text=item.text,
                checksum=item.checksum,
                metadata=item.metadata,
                provenance=item.provenance,
            )
            for item in request.records
        ]
        return self.summarise_records(
            document_id=request.document_id,
            records=records,
            provider_name=request.provider,
            requested_model=request.model,
            template_version=request.template_version,
            max_summary_tokens_per_record=request.max_summary_tokens_per_record,
        )

    def summarise_records(
        self,
        *,
        document_id: str,
        records: list[ParagraphRecord],
        provider_name: str,
        requested_model: str | None,
        template_version: str,
        max_summary_tokens_per_record: int,
    ) -> SummaryPipelineResult:
        template = get_template(template_version)
        provider = get_provider(provider_name, self.settings)
        model = resolve_model(provider, requested_model)
        artifact_id = make_artifact_id(document_id, [record.record_id for record in records])
        summaries: list[ParagraphSummary] = []
        pending: list[tuple[ParagraphRecord, str, str]] = []
        total_usage = Usage()
        cache_hits = 0

        for record in records:
            input_text_hash = sha256_text(record.text)
            cache_key = build_cache_key(
                input_text_hash=input_text_hash,
                summary_style=SUMMARY_STYLE,
                template_version=template_version,
                provider=provider.name,
                model=model,
                redaction_version=self.settings.redaction_version,
                max_summary_tokens=max_summary_tokens_per_record,
            )
            cached = self.repository.get_cache(cache_key)
            if cached:
                summary_text, usage = cached
                cache_hits += 1
                total_usage = total_usage.plus(usage)
                summaries.append(
                    ParagraphSummary(
                        document_id=document_id,
                        record_id=record.record_id,
                        source_ref=record.source_ref,
                        input_text_hash=input_text_hash,
                        summary=summary_text,
                        summary_style=SUMMARY_STYLE,
                        template_version=template_version,
                        provider=provider.name,
                        model=model,
                        cache_hit=True,
                        status="completed",
                        usage=usage,
                        metadata=redact_metadata(record.metadata, raw_text=record.text),
                        provenance=record.provenance,
                    )
                )
            else:
                pending.append((record, input_text_hash, cache_key))

        provider_requests = [
            ProviderParagraphRequest(
                record_id=record.record_id,
                source_ref=record.source_ref,
                text=redact_text(record.text),
                input_text_hash=input_hash,
                max_summary_tokens=max_summary_tokens_per_record,
            )
            for record, input_hash, _ in pending
        ]
        batches = TokenBudgetPacker(
            target_input_tokens=self._target_token_budget(provider.name),
            chars_per_token=self.settings.token_chars_per_token,
        ).pack(provider_requests)
        result_by_record_id = {}
        usage_by_record_id = {}
        provider_usage_total = Usage()
        batches_processed = 0

        for batch in batches:
            try:
                batch_result = provider.generate_paragraph_summaries(
                    records=batch.records,
                    template=template,
                    model=model,
                )
            except ProviderError as exc:
                for req in batch.records:
                    result_by_record_id[req.record_id] = ("", "failed", exc.error_code)
                    usage_by_record_id[req.record_id] = Usage()
                batches_processed += 1
                continue
            batches_processed += 1
            provider_usage_total = provider_usage_total.plus(batch_result.usage)
            per_record_usage = _split_usage(batch_result.usage, max(1, len(batch.records)))
            for item in batch_result.results:
                result_by_record_id[item.record_id] = (item.summary, item.status, item.error_code)
                usage_by_record_id[item.record_id] = per_record_usage

        pending_by_id = {
            record.record_id: (record, input_hash, cache_key)
            for record, input_hash, cache_key in pending
        }
        for record_id, (record, input_hash, cache_key) in pending_by_id.items():
            summary_text, status, error_code = result_by_record_id.get(
                record_id,
                ("", "failed", "MISSING_PROVIDER_RESULT"),
            )
            usage = usage_by_record_id.get(record_id, Usage())
            total_usage = total_usage.plus(usage)
            summary = ParagraphSummary(
                document_id=document_id,
                record_id=record.record_id,
                source_ref=record.source_ref,
                input_text_hash=input_hash,
                summary=summary_text,
                summary_style=SUMMARY_STYLE,
                template_version=template_version,
                provider=provider.name,
                model=model,
                cache_hit=False,
                status=status,
                usage=usage,
                metadata=redact_metadata(record.metadata, raw_text=record.text),
                provenance=record.provenance,
                error_code=error_code,
            )
            summaries.append(summary)
            if status == "completed" and summary_text:
                self.repository.put_cache(
                    cache_key=cache_key,
                    input_text_hash=input_hash,
                    summary_text=summary_text,
                    summary_style=SUMMARY_STYLE,
                    template_version=template_version,
                    provider=provider.name,
                    model=model,
                    usage=usage,
                )

        record_order = {record.record_id: index for index, record in enumerate(records)}
        summaries.sort(key=lambda item: record_order[item.record_id])
        output_path = write_jsonl_artifact(
            artifact_dir=self.settings.summary_artifact_dir,
            document_id=document_id,
            summaries=summaries,
        )
        self.repository.create_artifact(
            artifact_id=artifact_id,
            document_id=document_id,
            output_path=output_path,
            record_count=len(summaries),
            provider=provider.name,
            model=model,
            template_version=template_version,
        )
        for summary in summaries:
            self.repository.record_summary(artifact_id, summary)

        completed = sum(1 for summary in summaries if summary.status == "completed")
        failed = len(summaries) - completed
        log_event(
            self.logger,
            "paragraph_summary_artifact_created",
            artifact_id=artifact_id,
            document_id=document_id,
            provider=provider.name,
            model=model,
            template_version=template_version,
            records_received=len(records),
            records_completed=completed,
            records_failed=failed,
            cache_hits=cache_hits,
        )
        response = ParagraphSummaryArtifactResponse(
            artifact_id=artifact_id,
            document_id=document_id,
            output_path=str(output_path),
            records_received=len(records),
            records_completed=completed,
            records_failed=failed,
            cache_hits=cache_hits,
            provider=provider.name,
            model=model,
            template_version=template_version,
            usage=UsageResponse(**total_usage.__dict__),
            batches_processed=batches_processed,
        )
        return SummaryPipelineResult(response=response, artifact_path=str(output_path))

    def _target_token_budget(self, provider_name: str) -> int:
        if provider_name == "gemini":
            return self.settings.gemini_safe_input_token_target
        return self.settings.gemini_safe_input_token_target


def _split_usage(usage: Usage, count: int) -> Usage:
    return Usage(
        input_tokens=usage.input_tokens // count,
        output_tokens=usage.output_tokens // count,
        total_tokens=usage.total_tokens // count,
        estimated_cost_usd=round(usage.estimated_cost_usd / count, 8),
    )

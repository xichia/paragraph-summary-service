from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.models.requests import ParagraphSummaryRequest


class RequestLimitError(ValueError):
    pass


def validate_paragraph_request_limits(request: ParagraphSummaryRequest, settings: Settings) -> None:
    if len(request.records) > settings.max_records_per_request:
        raise RequestLimitError(f"record count exceeds limit of {settings.max_records_per_request}")
    total_chars = 0
    for record in request.records:
        text_len = len(record.text)
        if text_len > settings.max_record_chars:
            raise RequestLimitError(
                f"record {record.record_id!r} exceeds per-record character limit"
            )
        total_chars += text_len
    if total_chars > settings.max_total_chars:
        raise RequestLimitError(
            f"request exceeds total character limit of {settings.max_total_chars}"
        )

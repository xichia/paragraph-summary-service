from __future__ import annotations

from dataclasses import dataclass

from paragraph_summary_service.models.domain import ProviderParagraphRequest
from paragraph_summary_service.usage.tokens import estimate_tokens


@dataclass(frozen=True)
class PackedBatch:
    records: list[ProviderParagraphRequest]
    estimated_input_tokens: int


class TokenBudgetPacker:
    """Greedy packer for one-provider-call batches.

    It does not sleep or enforce wall-clock rate limits. A scheduler can call this once per minute
    when using one-request-per-minute provider workflows.
    """

    def __init__(self, target_input_tokens: int, chars_per_token: int = 4):
        self.target_input_tokens = target_input_tokens
        self.chars_per_token = chars_per_token

    def pack(self, records: list[ProviderParagraphRequest]) -> list[PackedBatch]:
        batches: list[PackedBatch] = []
        current: list[ProviderParagraphRequest] = []
        current_tokens = 0
        for record in records:
            record_tokens = estimate_tokens(record.text, self.chars_per_token)
            if current and current_tokens + record_tokens > self.target_input_tokens:
                batches.append(PackedBatch(records=current, estimated_input_tokens=current_tokens))
                current = []
                current_tokens = 0
            current.append(record)
            current_tokens += record_tokens
        if current:
            batches.append(PackedBatch(records=current, estimated_input_tokens=current_tokens))
        return batches

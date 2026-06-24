from paragraph_summary_service.batching.minute_packer import TokenBudgetPacker
from paragraph_summary_service.models.domain import ProviderParagraphRequest


def test_token_packer_splits_by_budget():
    records = [
        ProviderParagraphRequest(f"r{i}", f"ref {i}", "x" * 20, "sha256:x", 48)
        for i in range(5)
    ]
    batches = TokenBudgetPacker(target_input_tokens=10, chars_per_token=4).pack(records)
    assert len(batches) >= 3
    assert sum(len(batch.records) for batch in batches) == 5

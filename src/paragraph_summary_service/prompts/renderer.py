from __future__ import annotations

import json

from paragraph_summary_service.models.domain import ProviderParagraphRequest
from paragraph_summary_service.prompts.templates import PromptTemplate


def render_batch_prompt(
    template: PromptTemplate,
    records: list[ProviderParagraphRequest],
) -> tuple[str, str]:
    safe_records = [
        {"record_id": record.record_id, "source_ref": record.source_ref, "text": record.text}
        for record in records
    ]
    return template.system_instruction, template.user_template.format(
        records_json=json.dumps(safe_records, ensure_ascii=False)
    )

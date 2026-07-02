from __future__ import annotations

import json
import os
from pathlib import Path

from paragraph_summary_service.models.domain import ParagraphSummary


def safe_document_slug(document_id: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in document_id)[:160]


def write_jsonl_artifact(*, artifact_dir: Path, document_id: str,
                         summaries: list[ParagraphSummary]) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    output_path = artifact_dir / f"{safe_document_slug(document_id)}.paragraph_summaries.jsonl"
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        for summary in summaries:
            handle.write(json.dumps(_summary_to_line(summary), sort_keys=True, ensure_ascii=False))
            handle.write("\n")
    os.replace(temp_path, output_path)
    return output_path


def _summary_to_line(summary: ParagraphSummary) -> dict:
    return {
        "artifact_id": summary.artifact_id,
        "document_id": summary.document_id,
        "record_id": summary.record_id,
        "source_ref": summary.source_ref,
        "input_text_hash": summary.input_text_hash,
        "summary": summary.summary,
        "summary_style": summary.summary_style,
        "template_version": summary.template_version,
        "provider": summary.provider,
        "model": summary.model,
        "cache_hit": summary.cache_hit,
        "status": summary.status,
        "runtime_mode": summary.runtime_mode,
        "usage": summary.usage.__dict__,
        "metadata": summary.metadata,
        "provenance": summary.provenance,
        "error_code": summary.error_code,
    }

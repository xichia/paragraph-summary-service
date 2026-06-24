from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from paragraph_summary_service.models.domain import ParagraphSummary, Usage
from paragraph_summary_service.storage.db import connect


class SummaryRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        return connect(self.db_path)

    def get_cache(self, cache_key: str) -> tuple[str, Usage] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT summary_text, usage_json FROM cache_entries WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
        if row is None:
            return None
        return row["summary_text"], Usage(**json.loads(row["usage_json"]))

    def put_cache(
        self,
        *,
        cache_key: str,
        input_text_hash: str,
        summary_text: str,
        summary_style: str,
        template_version: str,
        provider: str,
        model: str,
        usage: Usage,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache_entries (
                    cache_key, input_text_hash, summary_text, summary_style,
                    template_version, provider, model, usage_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    input_text_hash,
                    summary_text,
                    summary_style,
                    template_version,
                    provider,
                    model,
                    json.dumps(usage.__dict__, sort_keys=True),
                ),
            )

    def record_summary(self, artifact_id: str, summary: ParagraphSummary) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO summary_results (
                    artifact_id, document_id, record_id, source_ref, input_text_hash,
                    summary_text, summary_style, template_version, provider, model,
                    usage_json, cache_hit, status, error_code, metadata_json, provenance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    summary.document_id,
                    summary.record_id,
                    summary.source_ref,
                    summary.input_text_hash,
                    summary.summary,
                    summary.summary_style,
                    summary.template_version,
                    summary.provider,
                    summary.model,
                    json.dumps(summary.usage.__dict__, sort_keys=True),
                    1 if summary.cache_hit else 0,
                    summary.status,
                    summary.error_code,
                    json.dumps(summary.metadata, sort_keys=True, default=str),
                    summary.provenance,
                ),
            )

    def create_artifact(
        self,
        *,
        artifact_id: str,
        document_id: str,
        output_path: Path,
        record_count: int,
        provider: str,
        model: str,
        template_version: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO artifacts (
                    artifact_id, document_id, output_path, record_count,
                    provider, model, template_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact_id,
                    document_id,
                    str(output_path),
                    record_count,
                    provider,
                    model,
                    template_version,
                ),
            )

    def get_artifact_path(self, artifact_id: str) -> Path | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT output_path FROM artifacts WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()
        return None if row is None else Path(row["output_path"])

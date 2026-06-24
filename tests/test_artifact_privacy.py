import json
import sqlite3
from pathlib import Path

from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.models.requests import ParagraphSummaryRequest
from paragraph_summary_service.services.paragraph_summarise import ParagraphSummaryService

RAW_SENTINEL = "RAW_PARAGRAPH_SENTINEL_7f6c874b"


def test_raw_paragraph_text_stays_out_of_artifact_cache_metadata(tmp_path, caplog):
    raw_text = (
        "Stable retrieval sentence. "
        f"{RAW_SENTINEL} appears only in the source paragraph body."
    )
    settings = Settings(
        summary_db_path=tmp_path / "paragraph_summary.sqlite",
        summary_artifact_dir=tmp_path / "artifacts",
    )
    request = ParagraphSummaryRequest(
        document_id="doc_privacy",
        records=[
            {
                "record_id": "doc_privacy/page_0001/para_0001",
                "source_ref": "page 1, paragraph 1",
                "text": raw_text,
                "metadata": {
                    "nested": {
                        "note": "keep this source hint",
                        "paragraph_text": raw_text,
                    },
                    "page": 1,
                    "text": raw_text,
                },
            }
        ],
        provider="mock",
        model="mock-deterministic-v1",
        template_version="paragraph_sentence_batch_v1",
    )

    with caplog.at_level("INFO", logger="paragraph_summary_service"):
        result = ParagraphSummaryService(settings).summarise_request(request)

    artifact_text = Path(result.artifact_path).read_text(encoding="utf-8")
    artifact_lines = [json.loads(line) for line in artifact_text.splitlines()]

    assert artifact_lines == [
        {
            "cache_hit": False,
            "document_id": "doc_privacy",
            "error_code": None,
            "input_text_hash": artifact_lines[0]["input_text_hash"],
            "metadata": {
                "nested": {
                    "note": "keep this source hint",
                    "paragraph_text": "[REDACTED]",
                },
                "page": 1,
                "text": "[REDACTED]",
            },
            "model": "mock-deterministic-v1",
            "provider": "mock",
            "provenance": "deepreader",
            "record_id": "doc_privacy/page_0001/para_0001",
            "source_ref": "page 1, paragraph 1",
            "status": "completed",
            "summary": "Stable retrieval sentence.",
            "summary_style": "paragraph_sentence",
            "template_version": "paragraph_sentence_batch_v1",
            "usage": artifact_lines[0]["usage"],
        }
    ]
    assert "text" not in artifact_lines[0]
    assert RAW_SENTINEL not in artifact_text
    assert raw_text not in artifact_text
    assert RAW_SENTINEL not in caplog.text
    assert raw_text not in caplog.text

    database_text = _database_text(settings.summary_db_path)

    assert RAW_SENTINEL not in database_text
    assert raw_text not in database_text


def _database_text(db_path: Path) -> str:
    with sqlite3.connect(db_path) as conn:
        rows: list[str] = []
        for table in ("cache_entries", "summary_results", "artifacts"):
            table_rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            rows.extend(
                "|".join("" if value is None else str(value) for value in row)
                for row in table_rows
            )
    return "\n".join(rows)

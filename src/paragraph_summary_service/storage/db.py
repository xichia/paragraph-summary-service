from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS cache_entries (
    cache_key TEXT PRIMARY KEY,
    input_text_hash TEXT NOT NULL,
    summary_text TEXT NOT NULL,
    summary_style TEXT NOT NULL,
    template_version TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    usage_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS summary_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    input_text_hash TEXT NOT NULL,
    summary_text TEXT,
    summary_style TEXT NOT NULL,
    template_version TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    usage_json TEXT NOT NULL,
    cache_hit INTEGER NOT NULL,
    status TEXT NOT NULL,
    error_code TEXT,
    metadata_json TEXT NOT NULL,
    provenance TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    output_path TEXT NOT NULL,
    record_count INTEGER NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    template_version TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn

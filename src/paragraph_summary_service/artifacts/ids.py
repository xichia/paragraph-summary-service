from __future__ import annotations

import hashlib
import time

from paragraph_summary_service.artifacts.writer import safe_document_slug


def make_artifact_id(document_id: str, record_ids: list[str]) -> str:
    digest = hashlib.sha256("\n".join(record_ids).encode("utf-8")).hexdigest()[:12]
    millis = int(time.time() * 1000)
    return f"artifact_{safe_document_slug(document_id)}_{digest}_{millis}"

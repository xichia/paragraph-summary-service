from __future__ import annotations

import hashlib
import json


def normalize_text_for_hash(text: str) -> str:
    return "\n".join(
        line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ).strip()


def sha256_text(text: str) -> str:
    digest = hashlib.sha256(normalize_text_for_hash(text).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def build_cache_key(
    *,
    input_text_hash: str,
    summary_style: str,
    template_version: str,
    provider: str,
    model: str,
    redaction_version: str,
    max_summary_tokens: int,
) -> str:
    payload = {
        "input_text_hash": input_text_hash,
        "summary_style": summary_style,
        "template_version": template_version,
        "provider": provider,
        "model": model,
        "redaction_version": redaction_version,
        "max_summary_tokens": max_summary_tokens,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"cache:{digest}"

from __future__ import annotations

import json
from typing import Any

import httpx

from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.models.domain import (
    ProviderBatchResult,
    ProviderParagraphRequest,
    ProviderParagraphResult,
    Usage,
)
from paragraph_summary_service.prompts.renderer import render_batch_prompt
from paragraph_summary_service.prompts.templates import PromptTemplate
from paragraph_summary_service.providers.base import ProviderNotEnabledError, ProviderResponseError


class GeminiProvider:
    name = "gemini"
    default_model = "gemini-2.5-flash-lite"

    def __init__(self, settings: Settings):
        self.settings = settings

    def generate_paragraph_summaries(
        self,
        *,
        records: list[ProviderParagraphRequest],
        template: PromptTemplate,
        model: str,
    ) -> ProviderBatchResult:
        if not self.settings.allow_external_provider_calls:
            raise ProviderNotEnabledError("external provider calls are disabled")
        if not self.settings.gemini_api_key:
            raise ProviderNotEnabledError("GEMINI_API_KEY is required for Gemini provider")

        system_prompt, user_prompt = render_batch_prompt(template, records)
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={self.settings.gemini_api_key}"
        )
        payload: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.0},
        }
        try:
            response = httpx.post(url, json=payload, timeout=self.settings.gemini_timeout_seconds)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderResponseError(f"Gemini HTTP error: {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise ProviderResponseError("Gemini request failed") from exc

        data = response.json()
        text = _extract_text(data)
        parsed = _parse_json_text(text)
        results = _parse_results(
            parsed,
            expected_record_ids={record.record_id for record in records},
        )
        return ProviderBatchResult(
            results=results,
            usage=_parse_usage(data),
            raw_provider_metadata={},
        )


def _extract_text(data: dict[str, Any]) -> str:
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderResponseError("Gemini response did not contain expected text") from exc


def _parse_json_text(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderResponseError("Gemini response was not valid JSON") from exc


def _parse_results(
    parsed: dict[str, Any],
    expected_record_ids: set[str],
) -> list[ProviderParagraphResult]:
    summaries = parsed.get("summaries")
    if not isinstance(summaries, list):
        raise ProviderResponseError("Gemini JSON missing summaries array")
    results: list[ProviderParagraphResult] = []
    seen: set[str] = set()
    for item in summaries:
        if not isinstance(item, dict):
            continue
        record_id = str(item.get("record_id", ""))
        if record_id not in expected_record_ids:
            raise ProviderResponseError(f"Gemini returned unexpected record_id: {record_id}")
        summary = str(item.get("summary", "")).strip()
        status = str(item.get("status", "completed"))
        if not summary and status == "completed":
            raise ProviderResponseError(f"Gemini returned empty summary for {record_id}")
        seen.add(record_id)
        results.append(ProviderParagraphResult(record_id=record_id, summary=summary, status=status))
    missing = expected_record_ids - seen
    if missing:
        raise ProviderResponseError(f"Gemini response missing record_ids: {sorted(missing)[:3]}")
    return results


def _parse_usage(data: dict[str, Any]) -> Usage:
    metadata = data.get("usageMetadata", {}) if isinstance(data, dict) else {}
    input_tokens = int(metadata.get("promptTokenCount", 0) or 0)
    output_tokens = int(metadata.get("candidatesTokenCount", 0) or 0)
    total_tokens = int(metadata.get("totalTokenCount", input_tokens + output_tokens) or 0)
    return Usage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=0.0,
    )

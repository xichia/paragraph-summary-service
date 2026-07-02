import json
from pathlib import Path

from paragraph_summary_service.config.settings import Settings
from paragraph_summary_service.models.requests import ParagraphSummaryRequest
from paragraph_summary_service.services.paragraph_summarise import ParagraphSummaryService


def test_gemini_success_status_counts_as_completed(tmp_path, monkeypatch):
    class FakeGeminiResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
                                        {
                                            "summaries": [
                                                {
                                                    "record_id": "doc_live/page_0001/para_0001",
                                                    "summary": (
                                                        "Stable paragraph identifiers enable "
                                                        "retrieval systems to link generated "
                                                        "summaries to source text."
                                                    ),
                                                    "status": "success",
                                                }
                                            ]
                                        }
                                    )
                                }
                            ]
                        }
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": 10,
                    "candidatesTokenCount": 7,
                    "totalTokenCount": 17,
                },
            }

    def fake_post(url, json, timeout):
        return FakeGeminiResponse()

    monkeypatch.setattr("paragraph_summary_service.providers.gemini.httpx.post", fake_post)
    settings = Settings(
        summary_db_path=tmp_path / "summary.sqlite",
        summary_artifact_dir=tmp_path / "artifacts",
        allow_external_provider_calls=True,
        gemini_api_key="fake-test-key",
    )
    request = ParagraphSummaryRequest(
        document_id="doc_live",
        records=[
            {
                "record_id": "doc_live/page_0001/para_0001",
                "source_ref": "page 1, paragraph 1",
                "text": (
                    "Stable paragraph identifiers enable retrieval systems to link generated "
                    "summaries to source text while maintaining citation provenance."
                ),
                "metadata": {"page": 1},
            }
        ],
        provider="gemini",
        model="gemini-3.1-flash-lite",
        template_version="paragraph_sentence_batch_v1",
    )

    result = ParagraphSummaryService(settings).summarise_request(request)
    artifact_text = Path(result.artifact_path).read_text(encoding="utf-8")
    artifact_line = json.loads(artifact_text)

    assert result.response.records_completed == 1
    assert result.response.records_failed == 0
    assert result.response.provider == "gemini"
    assert result.response.model == "gemini-3.1-flash-lite"
    assert result.response.batches_processed == 1
    assert artifact_line["status"] == "completed"
    assert artifact_line["artifact_id"] == result.response.artifact_id
    assert artifact_line["runtime_mode"] == "live"
    assert '"status": "success"' not in artifact_text

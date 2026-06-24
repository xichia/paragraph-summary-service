import json
from pathlib import Path


def _request():
    return {
        "document_id": "doc_001",
        "records": [
            {
                "record_id": "doc_001/page_0001/para_0001",
                "source_ref": "page 1, paragraph 1",
                "text": (
                    "The service must not log raw source text. "
                    "It should use hashes and IDs instead."
                ),
                "metadata": {"page": 1},
            },
            {
                "record_id": "doc_001/page_0001/para_0002",
                "source_ref": "page 1, paragraph 2",
                "text": (
                    "One-sentence summaries improve retrieval by giving dense text "
                    "a concise conceptual representation."
                ),
                "metadata": {"page": 1},
            },
        ],
        "provider": "mock",
        "model": "mock-deterministic-v1",
        "template_version": "paragraph_sentence_batch_v1",
    }


def test_paragraph_endpoint_creates_jsonl_artifact(client):
    response = client.post("/paragraph-summaries", json=_request())
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["records_completed"] == 2
    assert data["records_failed"] == 0
    path = Path(data["output_path"])
    assert path.exists()
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 2
    assert lines[0]["record_id"] == "doc_001/page_0001/para_0001"
    assert "text" not in lines[0]
    assert lines[0]["summary"].endswith(".")


def test_second_request_is_cache_hit(client):
    first = client.post("/paragraph-summaries", json=_request())
    assert first.status_code == 200
    second = client.post("/paragraph-summaries", json=_request())
    assert second.status_code == 200
    assert second.json()["cache_hits"] == 2

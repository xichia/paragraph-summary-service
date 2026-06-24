def test_rejects_duplicate_record_ids(client):
    payload = {
        "document_id": "doc",
        "records": [
            {"record_id": "same", "text": "First paragraph."},
            {"record_id": "same", "text": "Second paragraph."},
        ],
    }
    response = client.post("/paragraph-summaries", json=payload)
    assert response.status_code == 422


def test_rejects_unknown_template(client):
    payload = {
        "document_id": "doc",
        "records": [{"record_id": "r1", "text": "A paragraph."}],
        "template_version": "missing_template",
    }
    response = client.post("/paragraph-summaries", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNKNOWN_TEMPLATE"

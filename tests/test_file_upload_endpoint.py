def test_file_upload_endpoint(client):
    files = {
        "file": (
            "sample.md",
            b"# Demo\n\nFirst paragraph.\n\nSecond paragraph.",
            "text/markdown",
        )
    }
    response = client.post("/paragraph-summaries/from-file", files=files, data={"provider": "mock"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["records_completed"] == 2
    assert data["document_id"].startswith("upload_")

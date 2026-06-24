from paragraph_summary_service.splitters.lightweight import split_uploaded_text


def test_markdown_splitter_produces_provisional_records():
    content = "# Title\n\nFirst paragraph.\n\n## Section\n\nSecond paragraph."
    document_id, records = split_uploaded_text(
        filename="sample.md",
        content=content,
        content_type="text/markdown",
    )
    assert document_id.startswith("upload_")
    assert len(records) == 2
    assert records[0].record_id.startswith("standalone/")
    assert records[0].metadata["heading_path"] == ["Title"]
    assert records[1].metadata["heading_path"] == ["Title", "Section"]
    assert records[0].provenance == "llm_summariser_lightweight_splitter"

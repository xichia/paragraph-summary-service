# DeepReader Integration

DeepReader should call the record-based endpoint after it has ingested a document and produced canonical paragraph records.

```http
POST /paragraph-summaries
```

```json
{
  "document_id": "deepreader_doc_001",
  "records": [
    {
      "record_id": "deepreader_doc_001/page_0001/para_0003",
      "source_ref": "page 1, paragraph 3",
      "text": "Original paragraph...",
      "checksum": "sha256:...",
      "metadata": {"page": 1, "section": "Introduction"},
      "provenance": "deepreader"
    }
  ],
  "provider": "gemini",
  "model": "gemini-3.1-flash-lite",
  "template_version": "paragraph_sentence_batch_v1"
}
```

For local testing and CI, use:

```json
{
  "provider": "mock",
  "model": "mock-deterministic-v1"
}
```

The returned JSONL artifact preserves DeepReader IDs and source references. DeepReader can index the generated sentence as a secondary retrieval field while continuing to cite the original source record as evidence.

## Integration contract

DeepReader remains responsible for:

```text
file ingestion
canonical record IDs
source references
source hashes
retrieval indexes
citations
evidence packets
```

Paragraph Summary Service is responsible for:

```text
Gemini-backed one-sentence summaries
prompt template versioning
provider abstraction
redaction before provider submission
text-hash caching
usage accounting
JSONL artifact writing
safe logs
```

## Recommended DeepReader behavior

DeepReader should treat the summary artifact as an enrichment sidecar:

```text
original paragraph text: citation evidence and primary source field
one-sentence summary: secondary retrieval field
record_id/source_ref: join keys back to the original paragraph
```

If the summariser service is unavailable, DeepReader should continue to operate using its local/default summarisation and retrieval behavior.

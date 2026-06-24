# DeepReader Adapter Contract

This service expects DeepReader to remain the canonical owner of ingestion, paragraph segmentation, source references, retrieval, citations, and original paragraph text.

Paragraph Summary Service only generates one-sentence paragraph summary artifacts for records that DeepReader has already created.

## Canonical endpoint

POST /paragraph-summaries

## Request shape

Example request:

{
  "document_id": "doc_001",
  "records": [
    {
      "record_id": "doc_001/page_0001/para_0001",
      "source_ref": "page 1, paragraph 1",
      "text": "Paragraph text...",
      "checksum": "sha256:abc123",
      "metadata": {
        "page": 1,
        "section": "Introduction"
      },
      "provenance": "deepreader"
    }
  ],
  "provider": "mock",
  "model": "mock-deterministic-v1",
  "template_version": "paragraph_sentence_batch_v1"
}

## Required fields

Each request must include document_id and records.

Each record must include record_id, source_ref, and text.

## Recommended fields

Each record should include checksum, metadata, and provenance.

## Stable identifiers

record_id should be stable across runs for the same paragraph. DeepReader should generate and own this value.

Recommended pattern:

<document_id>/page_<page_number>/para_<paragraph_number>

Example:

doc_001/page_0001/para_0001

## Source references

source_ref should be human-readable and citation-friendly.

Examples:

page 1, paragraph 1
section "Risk Factors", paragraph 3
slide 4, bullet group 2

## Checksums

checksum should identify the original paragraph text as known to DeepReader.

Recommended format:

sha256:<hex_digest>

The service also computes its own input_text_hash for cache and artifact output.

## Metadata

Metadata may include structured non-sensitive context such as page number, section name, heading path, or document type.

Text-like metadata fields are redacted before persistence. Do not rely on this service to preserve long free-text metadata.

## Output artifact

The service writes JSONL sidecar artifacts with one line per paragraph summary.

The artifact includes document_id, record_id, source_ref, input_text_hash, summary, summary_style, template_version, provider, model, cache_hit, status, metadata, and usage.

Raw paragraph text is not written to the artifact by default.

## Integration responsibility split

DeepReader owns ingestion, paragraph splitting, canonical record IDs, source references, original text storage, retrieval, citations, and evidence inspection.

Paragraph Summary Service owns paragraph-summary generation, provider abstraction, prompt templates, text-hash cache, redaction before persistence, usage accounting, and JSONL artifact writing.

## File upload endpoint

POST /paragraph-summaries/from-file

This endpoint is only for local demos and standalone testing. It creates provisional records and should not be used as the canonical DeepReader integration path.

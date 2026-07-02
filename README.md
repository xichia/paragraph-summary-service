# Paragraph Summary Service

`paragraph-summary-service` generates **Gemini-backed one-sentence paragraph summary artifacts** for DeepReader retrieval enhancement.

DeepReader keeps the original paragraph records as the citation-grade evidence. This service takes those already-ingested paragraph records, asks a configured LLM provider to produce one sentence per paragraph, then writes a JSONL sidecar artifact that DeepReader can index alongside the original text.

Gemini is the **primary real provider path** for the project. The deterministic mock provider exists so the API, cache, artifact writer, redaction, batching, tests, CI, and local demos can run without network access or API keys.

## Companion service boundaries

Paragraph Summary Service is **DeepReader's companion summary execution service**, not a RAG/search/dashboard/ingestion system.

```text
DeepReader stable paragraph records
→ Paragraph Summary Service
→ Gemini one-sentence paragraph summaries
→ JSONL sidecar artifact
→ DeepReader indexes original text + summaries
```

### What Paragraph Summary Service owns

- provider/mock paragraph summary generation execution
- prompt/provider abstraction
- batching (token-aware packing)
- redaction (input text + metadata)
- cache behavior (text-hash-based SQLite cache)
- usage metadata (token counts, estimated cost)
- provider safety (opt-in external calls, safe defaults)
- JSONL/sidecar artifact generation

### What Paragraph Summary Service does NOT own

This service is intentionally narrow. DeepReader remains the canonical owner of:

- document ingestion and source records
- retrieval, search, and RAG pipelines
- QA citations and evidence packets
- frontend dashboard and inspection tooling
- summary indexing and secondary field management

### Provider safety default

Live provider calls are opt-in. The safe default for reviewers, tests, and CI:

```env
LLM_PROVIDER=mock
ALLOW_EXTERNAL_PROVIDER_CALLS=false
```

This keeps the project reviewable without credentials, network access, or quota. See
[docs/DEMO_WORKFLOW.md](docs/DEMO_WORKFLOW.md) for the reviewer-safe offline workflow.

## Provider model

There are two provider paths:

| Provider | Role | Network/API key | Intended use |
| --- | --- | --- | --- |
| `gemini` | Primary real provider | Yes | Actual one-sentence paragraph summary generation |
| `mock` | Deterministic offline provider | No | Tests, CI, local demos, pipeline validation |

The service is safe-by-default:

```env
LLM_PROVIDER=mock
ALLOW_EXTERNAL_PROVIDER_CALLS=false
```

That default does **not** mean mock is the product goal. It means a reviewer can run the full pipeline locally without credentials, and tests never spend quota.

Production-style Gemini mode must be explicit:

```env
LLM_PROVIDER=gemini
ALLOW_EXTERNAL_PROVIDER_CALLS=true
GEMINI_API_KEY=your_authorised_key_here
GEMINI_MODEL=gemini-3.1-flash-lite
GEMINI_INPUT_TPM_LIMIT=250000
GEMINI_SAFE_INPUT_TOKEN_TARGET=225000
GEMINI_REQUESTS_PER_MINUTE=1
GEMINI_TIMEOUT_SECONDS=90
```

Use only API keys and projects you are authorised to use, and configure token/request limits to match the provider dashboard for your account or project.

## Core flow

```text
DeepReader records ─┐
                    ├─> shared paragraph summary pipeline ─> JSONL sidecar artifact
File upload adapter ┘
```

The canonical integration endpoint accepts already-ingested DeepReader-style paragraph records:

```http
POST /paragraph-summaries
```

The standalone demo endpoint accepts `.txt` and `.md` uploads, creates provisional records, and uses the same summary pipeline:

```http
POST /paragraph-summaries/from-file
```

The file upload endpoint is a convenience adapter, not a replacement for DeepReader ingestion. DeepReader should remain the source of truth for canonical record IDs, source references, hashes, and citations.

## Output artifact

Artifacts are written under `SUMMARY_ARTIFACT_DIR`, defaulting to:

```text
output/paragraph_summaries/<document_id>.paragraph_summaries.jsonl
```

Each JSONL line contains record IDs, source references, text hashes, summary text, provider/model metadata, template version, cache status, usage, status, and provenance. Raw paragraph text is not written to artifacts by default.

Example line:

```json
{
  "artifact_id": "artifact_doc_001_6204e91faa92_1782289345276",
  "document_id": "doc_001",
  "record_id": "doc_001/page_0001/para_0001",
  "source_ref": "page 1, paragraph 1",
  "input_text_hash": "sha256:abc123...",
  "summary": "The paragraph explains how stable paragraph records improve retrieval while preserving citation evidence.",
  "summary_style": "paragraph_sentence",
  "template_version": "paragraph_sentence_batch_v1",
  "provider": "gemini",
  "model": "gemini-3.1-flash-lite",
  "cache_hit": false,
  "status": "completed",
  "runtime_mode": "mock",
  "provenance": "deepreader"
}
```

## Quick start with offline mock mode

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
uvicorn paragraph_summary_service.api.app:create_app --factory --reload
```

In another terminal:

```bash
curl -X POST http://localhost:8000/paragraph-summaries \
  -H "Content-Type: application/json" \
  -d @examples/paragraph_request.json
```

Upload demo file:

```bash
curl -F "file=@examples/sample.md" \
  -F "provider=mock" \
  -F "template_version=paragraph_sentence_batch_v1" \
  http://localhost:8000/paragraph-summaries/from-file
```

Download the generated artifact:

```bash
curl http://localhost:8000/artifacts/<artifact_id>
```


## Local demo transcript

The default local path uses the deterministic mock provider, so the service can be exercised without network access, quota usage, or API keys.

Start the API server:

```bash
.venv/bin/uvicorn paragraph_summary_service.api.app:create_app --factory --reload
```

Check service health:

```bash
curl -sS http://localhost:8000/health | jq
```

Example response:

```json
{
  "status": "ok",
  "service": "Paragraph Summary Service",
  "version": "0.1.1",
  "provider_default": "mock",
  "external_provider_calls_enabled": false
}
```

Generate paragraph summary artifacts from canonical DeepReader-shaped records:

```bash
curl -sS -X POST http://localhost:8000/paragraph-summaries \
  -H "Content-Type: application/json" \
  -d @examples/paragraph_request.json | jq
```

First run example:

```json
{
  "artifact_id": "artifact_doc_001_6204e91faa92_1782289345276",
  "document_id": "doc_001",
  "output_path": "output/paragraph_summaries/doc_001.paragraph_summaries.jsonl",
  "records_received": 2,
  "records_completed": 2,
  "records_failed": 0,
  "records_skipped": 0,
  "cache_hits": 0,
  "provider": "mock",
  "model": "mock-deterministic-v1",
  "template_version": "paragraph_sentence_batch_v1",
  "runtime_mode": "mock",
  "created_at": "2026-07-02T11:15:00Z",
  "usage": {
    "input_tokens": 66,
    "output_tokens": 42,
    "total_tokens": 108,
    "estimated_cost_usd": 0.0
  },
  "batches_processed": 1
}
```

Inspect the generated JSONL sidecar artifact:

```bash
cat output/paragraph_summaries/doc_001.paragraph_summaries.jsonl | jq -c .
```

Example JSONL line:

```json
{
  "artifact_id": "artifact_doc_001_6204e91faa92_1782289345276",
  "cache_hit": false,
  "document_id": "doc_001",
  "error_code": null,
  "input_text_hash": "sha256:a9dc3322bf37fa60292b5a71d4e675de3b80a9e2a12b7cb05f3509b666ed4546",
  "metadata": {
    "page": 1,
    "section": "Safety Model"
  },
  "model": "mock-deterministic-v1",
  "provenance": "deepreader",
  "provider": "mock",
  "record_id": "doc_001/page_0001/para_0001",
  "runtime_mode": "mock",
  "source_ref": "page 1, paragraph 1",
  "status": "completed",
  "summary": "The service must not log raw source text.",
  "summary_style": "paragraph_sentence",
  "template_version": "paragraph_sentence_batch_v1",
  "usage": {
    "estimated_cost_usd": 0.0,
    "input_tokens": 33,
    "output_tokens": 21,
    "total_tokens": 54
  }
}
```

Run the same request again to demonstrate cache reuse:

```bash
curl -sS -X POST http://localhost:8000/paragraph-summaries \
  -H "Content-Type: application/json" \
  -d @examples/paragraph_request.json | jq
```

Cache-hit response excerpt:

```json
{
  "records_received": 2,
  "records_completed": 2,
  "records_failed": 0,
  "cache_hits": 2,
  "provider": "mock",
  "model": "mock-deterministic-v1",
  "template_version": "paragraph_sentence_batch_v1",
  "batches_processed": 0
}
```

The artifact contains stable IDs, hashes, summaries, provenance, provider/model details, status, usage, and redacted metadata. It does not include raw paragraph text.

## Gemini mode

Create `.env` from `.env.example`, then enable Gemini intentionally:

```bash
cp .env.example .env
```

```env
LLM_PROVIDER=gemini
ALLOW_EXTERNAL_PROVIDER_CALLS=true
GEMINI_API_KEY=your_authorised_key_here
GEMINI_MODEL=gemini-3.1-flash-lite
GEMINI_INPUT_TPM_LIMIT=250000
GEMINI_SAFE_INPUT_TOKEN_TARGET=225000
GEMINI_REQUESTS_PER_MINUTE=1
```

Then call the same `/paragraph-summaries` endpoint with `provider: "gemini"` or omit the provider field if your request schema is configured to default to the environment provider in a future version.

The current implementation packs records by estimated input tokens and targets `GEMINI_SAFE_INPUT_TOKEN_TARGET`, leaving margin below `GEMINI_INPUT_TPM_LIMIT` for prompt overhead, tokenizer mismatch, and response tokens.

## Example request

```json
{
  "document_id": "doc_001",
  "records": [
    {
      "record_id": "doc_001/page_0001/para_0001",
      "source_ref": "page 1, paragraph 1",
      "text": "The original paragraph text...",
      "checksum": "sha256:abc123",
      "metadata": {"page": 1, "section": "Introduction"},
      "provenance": "deepreader"
    }
  ],
  "provider": "gemini",
  "model": "gemini-3.1-flash-lite",
  "template_version": "paragraph_sentence_batch_v1"
}
```

For offline local testing, use `provider: "mock"` and `model: "mock-deterministic-v1"`.

## Example response

```json
{
  "artifact_id": "artifact_doc_001_...",
  "document_id": "doc_001",
  "output_path": "output/paragraph_summaries/doc_001.paragraph_summaries.jsonl",
  "records_received": 1,
  "records_completed": 1,
  "records_failed": 0,
  "records_skipped": 0,
  "cache_hits": 0,
  "provider": "gemini",
  "model": "gemini-3.1-flash-lite",
  "template_version": "paragraph_sentence_batch_v1",
  "runtime_mode": "live",
  "created_at": "2026-07-02T11:15:00Z",
  "usage": {
    "input_tokens": 12,
    "output_tokens": 8,
    "total_tokens": 20,
    "estimated_cost_usd": 0.0
  },
  "batches_processed": 1
}
```

## Safety model

Logs may include artifact IDs, document IDs, provider names, model names, template versions, text hashes, record counts, cache hit counts, duration, and status.

Logs must not include raw paragraph text, full prompts, API keys, credentials, or unredacted sensitive metadata.

External LLM calls require both:

```env
LLM_PROVIDER=gemini
ALLOW_EXTERNAL_PROVIDER_CALLS=true
```

and a configured `GEMINI_API_KEY`. This prevents accidental quota use during development, tests, and CI.

## Development

```bash
python3 -m pytest
python3 -m ruff check src tests
```

The tests are fully offline and use the deterministic mock provider.

## Docker

```bash
docker compose up --build
```

See `docs/architecture.md`, `docs/gemini-provider.md`, and `docs/deepreader-integration.md` for design notes.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

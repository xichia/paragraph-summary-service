# Architecture

Paragraph Summary Service turns DeepReader-style paragraph records into one-sentence summary artifacts.

## Purpose

The project exists to generate **Gemini-backed paragraph summary sidecars** that DeepReader can use as a secondary retrieval field. The original paragraph text remains the evidence to cite; the generated sentence improves matching, concept coverage, and retrieval speed.

## Boundary

DeepReader is the canonical ingestion and retrieval system. It produces stable paragraph records, source references, hashes, and evidence packets. Paragraph Summary Service consumes paragraph records and produces summary sidecars.

The standalone file upload endpoint is intentionally limited. It creates deterministic provisional records for demos and testing, but those records are not citation-grade DeepReader records.

## Data flow

```text
POST /paragraph-summaries
→ validate records and limits
→ compute text hashes
→ check SQLite cache
→ redact provider input
→ pack records by token budget
→ call provider
→ validate one result per record
→ write JSONL artifact atomically
→ persist cache/results metadata
→ return artifact metadata
```

## Provider abstraction

Providers implement `ParagraphSummaryProvider`.

- `GeminiProvider`: primary real provider path for actual one-sentence paragraph summaries.
- `MockProvider`: deterministic offline provider for tests, CI, local demos, and pipeline validation.

The service defaults to mock mode for safety:

```env
LLM_PROVIDER=mock
ALLOW_EXTERNAL_PROVIDER_CALLS=false
```

Production-style Gemini mode must be enabled explicitly:

```env
LLM_PROVIDER=gemini
ALLOW_EXTERNAL_PROVIDER_CALLS=true
GEMINI_API_KEY=...
```

This keeps Gemini central to the product while preventing accidental external calls or quota use.

## Token-aware packing

The shared pipeline estimates input tokens and groups pending paragraph records into provider batches. In Gemini mode, the packer targets `GEMINI_SAFE_INPUT_TOKEN_TARGET`, which should be lower than the configured TPM limit to leave room for prompt overhead, tokenizer differences, and response tokens.

## Standalone file adapter

`POST /paragraph-summaries/from-file` converts TXT/Markdown into provisional records, then uses the same pipeline as DeepReader records. This endpoint exists for standalone use and portfolio demos. DeepReader integration should use the record-based endpoint.

## Caching

Cache keys include the normalized text hash, summary style, template version, provider, model, redaction version, and max output tokens. The cache does not depend on record ID, so DeepReader and standalone-upload records can share cached summaries when paragraph text is identical.

## Artifacts

Artifacts are written under `SUMMARY_ARTIFACT_DIR`. Caller-supplied file paths are not accepted. The artifact registry maps artifact IDs to safe local paths. Raw paragraph text is not written to JSONL summary artifacts by default.

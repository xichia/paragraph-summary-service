# Changelog

## Unreleased

- Added `created_at`, `records_skipped`, and `runtime_mode` fields to the
  `ParagraphSummaryArtifactResponse` API/CLI response envelope.
- `created_at` is an ISO 8601 UTC timestamp ending in `Z`, computed at response
  construction time.
- `records_skipped` is always `0` (no per-record skip behavior exists yet).
- `runtime_mode` reuses the same value already written to JSONL artifact lines
  (`"mock"`, `"live"`, or `"offline"`).
- Updated response shape test, Gemini status test, and docs to reflect the new
  response fields.
- No changes to provider behavior, cache semantics, runtime defaults, existing
  field names, types, or JSONL artifact schema.

## v0.3

- Added `artifact_id` to every JSONL artifact line (previously only in the response envelope).
- Added `runtime_mode` to every JSONL artifact line (`"mock"`, `"live"`, or `"offline"`),
  derived from existing provider/config state without runtime changes.
- Updated `docs/ARTIFACT_PROVENANCE.md` to reflect the two newly implemented fields.
- No changes to provider behavior, cache semantics, runtime defaults, existing field
  names, types, or response model fields.

## v0.2 planning/docs

- Clarified Paragraph Summary Service as DeepReader's companion summary
  execution service with explicit ownership boundaries (not a RAG/search/
  dashboard/ingestion system).
- Added docs/SUMMARY_JOB_LIFECYCLE.md design document defining lifecycle
  statuses, terminal/non-terminal states, partial success, retry semantics,
  and recovery patterns.
- Added docs/PROVIDER_ERROR_SEMANTICS.md design document defining retryable
  vs non-retryable provider error categories, error_code naming conventions,
  and condition-to-code mapping.
- Added docs/ARTIFACT_PROVENANCE.md documenting current and proposed artifact
  metadata fields, identification format, and schema stability expectations.
- Added docs/DEMO_WORKFLOW.md with a reviewer-safe offline/mock workflow that
  does not require service startup, live provider calls, OpenStax, or secrets
  inspection.
- Added docs/validation-log.md recording the validation commands run and
  explicitly confirming what was not performed.
- No runtime code, provider, cache, or default changes in this pass.

## 0.1.1

- Reframed the project as Gemini-backed one-sentence paragraph summary artifact generation for DeepReader retrieval enhancement.
- Clarified that Gemini is the primary real provider path.
- Clarified that the deterministic mock provider exists for offline tests, CI, demos, and pipeline validation.
- Added Gemini provider documentation and explicit production-style configuration notes.
- Kept safe local defaults: mock provider and external calls disabled.

## 0.1.0

- Initial paragraph-summary artifact service.
- Deterministic mock provider.
- DeepReader-shaped paragraph record API.
- Lightweight TXT/Markdown upload adapter.
- JSONL artifact writer and artifact download endpoint.
- SQLite cache and summary result persistence.
- Safe logging and redaction hooks.
- Optional Gemini provider adapter behind explicit opt-in.
- Offline pytest suite.

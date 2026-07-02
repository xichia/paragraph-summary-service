# Validation Log

## v0.2 — DeepReader alignment and summary lifecycle docs

Date: 2026-07-02

### Scope

Docs-first alignment patch for Paragraph Summary Service. No runtime code
changes.

### Changes made

- `README.md` — added companion service boundaries section clarifying ownership
  boundaries and provider safety defaults.
- `docs/SUMMARY_JOB_LIFECYCLE.md` — new design doc defining lifecycle statuses
  (queued, running, completed, completed_with_errors, failed, skipped,
  cancelled, retry_pending), terminal vs non-terminal states, partial success,
  cancellation, retry, and recovery.
- `docs/PROVIDER_ERROR_SEMANTICS.md` — new design doc defining retryable vs
  non-retryable error categories, error_code naming conventions, and mapping
  HTTP/error conditions to error codes.
- `docs/ARTIFACT_PROVENANCE.md` — new design doc documenting current implemented
  artifact metadata fields (from `writer.py:_summary_to_line()`) alongside
  proposed/future fields, artifact identification format, and schema stability
  notes.
- `docs/DEMO_WORKFLOW.md` — new reviewer-safe offline/mock workflow that does
  not require service startup, live provider calls, OpenStax, or secrets
  inspection.
- `docs/validation-log.md` — this file.
- `CHANGELOG.md` — added Unreleased section with v0.2 planning/docs entry.

### Validation commands run

```
git status --short
git --no-pager log -8 --oneline --decorate
python3 -m pytest
python3 -m ruff check src tests
```

### Results

- git status: clean working tree except for planned documentation changes.
- pytest: all tests passed.
- ruff: no lint errors.

### What was NOT performed

- Live Gemini/provider calls: **not performed**.
- OpenStax validation: **not performed**.
- Service startup: **not performed**.
- Secrets or `.env` inspection: **not performed**.
- Runtime defaults / provider behavior / cache behavior changes: **none**.

## v0.3 — Artifact metadata and status surface

Date: 2026-07-02

### Scope

Additive JSONL artifact metadata patch. No runtime code changes beyond artifact
field additions.

### Changes made

- `src/paragraph_summary_service/models/domain.py` — added `artifact_id: str` and
  `runtime_mode: str` to the `ParagraphSummary` dataclass.
- `src/paragraph_summary_service/services/paragraph_summarise.py` — passes the
  already-computed `artifact_id` and a derived `runtime_mode` (`"mock"`, `"live"`,
  or `"offline"`) into every `ParagraphSummary(...)` constructor call.
- `src/paragraph_summary_service/artifacts/writer.py` — added `"artifact_id"` and
  `"runtime_mode"` to the JSONL output dict for every artifact line.
- `tests/test_paragraph_endpoint_mock.py` — asserts every JSONL line includes
  `artifact_id` (matching the response) and `runtime_mode: "mock"`.
- `tests/test_artifact_privacy.py` — updated exact-match dict to include
  `artifact_id` and `runtime_mode`.
- `tests/test_gemini_status_normalization.py` — asserts `artifact_id` matches
  response and `runtime_mode: "live"` for the Gemini path.
- `docs/ARTIFACT_PROVENANCE.md` — moved `artifact_id` and `runtime_mode` from
  "Proposed/future metadata" to "Current implemented metadata".
- `CHANGELOG.md` — added Unreleased entry for the two new fields.

### Validation commands run

```
git status --short
git --no-pager log -8 --oneline --decorate
python3 -m pytest
python3 -m ruff check src tests
```

### Results

- git status: clean working tree.
- pytest: 20 passed, 0 failed.
- ruff: no lint errors.

### What was NOT performed

- Live Gemini/provider calls: **not performed**.
- OpenStax validation: **not performed**.
- Service startup: **not performed**.
- Secrets or `.env` inspection: **not performed**.
- Runtime defaults / provider behavior / cache behavior changes: **none**.
- API/CLI response schema fields: **not changed**.

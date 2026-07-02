# Demo Workflow (Reviewer-Safe / Offline / Mock)

This workflow lets a reviewer explore the project **without**:

- Starting the API or any service
- Making live Gemini/provider calls
- Running OpenStax validation
- Inspecting `.env` or secrets
- Using network access or API keys

All commands below are safe to run in a fresh clone.

## Prerequisites

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install project with dev dependencies
python3 -m pip install -e ".[dev]"
```

## 1. Verify repository state

```bash
git status --short
```

Expected: clean working tree (or list of uncommitted changes if you have local
edits).

```bash
git --no-pager log --oneline -5
```

Expected: recent commit history.

## 2. Run offline test suite

```bash
python3 -m pytest
```

All tests use the deterministic mock provider. No network access, no Gemini
calls, no API keys required.

Expected: all tests pass (collected N, passed N).

## 3. Run lint

```bash
python3 -m ruff check src tests
```

Expected: no lint errors.

## 4. Review documentation

Review the key design docs for the v0.2 alignment:

| Document | Purpose |
|---|---|
| [architecture.md](architecture.md) | System architecture and boundaries |
| [deepreader-adapter-contract.md](deepreader-adapter-contract.md) | Contract with DeepReader |
| [deepreader-integration.md](deepreader-integration.md) | Integration notes |
| [SUMMARY_JOB_LIFECYCLE.md](SUMMARY_JOB_LIFECYCLE.md) | Job lifecycle status semantics (design) |
| [PROVIDER_ERROR_SEMANTICS.md](PROVIDER_ERROR_SEMANTICS.md) | Provider error categories (design) |
| [ARTIFACT_PROVENANCE.md](ARTIFACT_PROVENANCE.md) | Artifact metadata and provenance |
| [DEMO_WORKFLOW.md](DEMO_WORKFLOW.md) | This document |

## 5. Inspect example data

```bash
# View example request payload
cat examples/paragraph_request.json

# View example upload document
cat examples/sample.md
```

## 6. Inspect example artifacts (if previously generated)

If the service was run previously and generated artifacts in `output/`:

```bash
# List any existing artifacts
ls -la output/paragraph_summaries/ 2>/dev/null || echo "No artifacts found (expected if service has not been started)"
```

## 7. Explore source structure

```bash
ls -R src/paragraph_summary_service/ | head -40
```

## What this workflow does NOT do

- Does NOT start the API server.
- Does NOT make live provider calls (Gemini or otherwise).
- Does NOT run OpenStax validation.
- Does NOT inspect `.env` files or secrets.
- Does NOT require network access.
- Does NOT spend API quota.

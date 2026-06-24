# Gemini Live Smoke Test

This smoke test verifies the real Gemini provider path with one tiny request.

It is manual by design. It must not run in CI and must not be required for local offline demos.

## Safety expectations

Mock remains the default provider for tests, CI, and local demos.

Gemini must only run when explicitly configured:

LLM_PROVIDER=gemini
ALLOW_EXTERNAL_PROVIDER_CALLS=true
GEMINI_API_KEY=...

Do not commit API keys, .env, generated artifacts, SQLite cache files, or local output directories.

## Start the service

Set environment variables:

export LLM_PROVIDER=gemini
export ALLOW_EXTERNAL_PROVIDER_CALLS=true
export GEMINI_API_KEY="your_authorised_key_here"
export GEMINI_MODEL=gemini-3.1-flash-lite
export GEMINI_REQUESTS_PER_MINUTE=1
export GEMINI_INPUT_TPM_LIMIT=250000
export GEMINI_SAFE_INPUT_TOKEN_TARGET=225000

Start Uvicorn:

.venv/bin/uvicorn paragraph_summary_service.api.app:create_app --factory --reload

## Run one request

In another terminal:

curl -sS -X POST http://localhost:8000/paragraph-summaries \
  -H "Content-Type: application/json" \
  -d @examples/gemini_smoke_request.json | jq

Expected result:

- records_received is 1
- records_completed is 1
- records_failed is 0
- provider is gemini
- model is gemini-3.1-flash-lite
- batches_processed is 1 on the first uncached run

## Inspect the artifact

cat output/paragraph_summaries/gemini_smoke_001.paragraph_summaries.jsonl | jq -c .

Confirm that the artifact includes:

- document_id
- record_id
- source_ref
- input_text_hash
- summary
- provider
- model
- status

Confirm that the artifact does not include raw paragraph text.

## Cache check

Run the same request a second time.

Expected result:

- cache_hits is 1
- batches_processed is 0

## Cleanup

Do not commit local generated output.

Recommended cleanup:

rm -rf output
rm -f .env

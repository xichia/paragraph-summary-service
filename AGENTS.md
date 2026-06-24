# AGENTS.md

This project is a Gemini-backed paragraph summary artifact service for DeepReader retrieval enhancement.

## Product direction

The service generates one-sentence summaries for already-ingested paragraph records and writes JSONL sidecar artifacts. DeepReader remains the canonical owner of ingestion, retrieval, citation, and source paragraph text.

The canonical integration endpoint is:

`POST /paragraph-summaries`

It accepts DeepReader-shaped paragraph records and produces summary artifacts without persisting raw paragraph text.

The file-upload endpoint:

`POST /paragraph-summaries/from-file`

is standalone/demo mode only. Do not treat it as the canonical DeepReader integration path.

## Provider rules

Gemini is the primary real provider and intended production path.

Mock mode must remain the default for local development, demos, tests, and CI.

Safe defaults:

```env
LLM_PROVIDER=mock
ALLOW_EXTERNAL_PROVIDER_CALLS=false

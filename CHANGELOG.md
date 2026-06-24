# Changelog

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

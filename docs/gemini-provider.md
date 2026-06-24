# Gemini Provider

Gemini is the primary real provider path for Paragraph Summary Service.

The service is designed to send many paragraph records to Gemini and receive exactly one sentence per record. The resulting JSONL artifact can then be indexed by DeepReader alongside the original paragraph text.

## Why Gemini is not enabled by default

Gemini is production-intended, but external provider calls are disabled by default so the project is safe to clone, test, run in CI, and demo without credentials or quota use.

Default local mode:

```env
LLM_PROVIDER=mock
ALLOW_EXTERNAL_PROVIDER_CALLS=false
```

Gemini mode:

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

The provider refuses to call Gemini unless external calls are explicitly enabled and an API key is present.

## Minute-packed request strategy

For paragraph summaries, a single request can contain many paragraph records. The service estimates token use and packs records until it approaches the configured safe input-token target.

Recommended starting point for a 250k input TPM allowance:

```env
GEMINI_INPUT_TPM_LIMIT=250000
GEMINI_SAFE_INPUT_TOKEN_TARGET=225000
GEMINI_REQUESTS_PER_MINUTE=1
```

The safe target is intentionally below the full limit to allow for:

- prompt instructions and JSON framing;
- tokenizer-estimation error;
- response tokens;
- provider-side enforcement variance;
- retries after malformed responses or transient errors.

## Expected response shape

The prompt asks Gemini to return valid JSON only:

```json
{
  "summaries": [
    {
      "record_id": "doc_001/page_0001/para_0001",
      "summary": "The paragraph explains how stable records preserve retrieval evidence.",
      "status": "completed"
    }
  ]
}
```

The service validates that every returned `record_id` was requested, every requested `record_id` is represented, and every completed record has a non-empty summary.

## Mock provider role

The mock provider is not the product goal. It exists to prove the rest of the system works:

```text
request validation
→ redaction
→ cache lookup
→ token packing
→ provider abstraction
→ JSONL artifact writing
→ artifact lookup
→ safe logging
```

Tests and CI should continue to use mock mode only.

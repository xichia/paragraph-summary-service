# Provider Error Semantics (Design)

This document defines the error category conventions for provider interactions in
Paragraph Summary Service.

**Status: design documentation.** The current implementation (`v0.1.x`) defines
three exception classes with hardcoded string `error_code` values:

| Exception | `error_code` |
|---|---|
| `ProviderError` | `"PROVIDER_ERROR"` |
| `ProviderNotEnabledError` | `"PROVIDER_NOT_ENABLED"` |
| `ProviderResponseError` | `"PROVIDER_RESPONSE_ERROR"` |

All Gemini API failures currently map to `"PROVIDER_RESPONSE_ERROR"` regardless
of root cause. The categories below are a design target for finer-grained
error classification.

## Retryable vs non-retryable

Errors in the **retryable** column may succeed on a subsequent attempt after a
suitable wait. Errors in the **non-retryable** column will not succeed on retry
without a configuration or input change.

| Category | `error_code` | Retryable | Description |
|---|---|---|---|
| Rate limit / quota | `RATE_LIMITED` | Yes | Provider returned 429 or similar rate-limit signal. |
| Timeout | `TIMEOUT` | Yes | Provider did not respond within the configured timeout. |
| Transient network | `TRANSIENT_NETWORK` | Yes | Connection reset, DNS failure, temporary routing error. |
| Malformed response | `MALFORMED_PROVIDER_RESPONSE` | No | Provider returned invalid JSON, unexpected schema, or missing fields. |
| Safety / refusal | `PROVIDER_REFUSAL` | No | Provider declined to generate summaries (safety filter, content policy). |
| Validation error | `VALIDATION_ERROR` | No | Request rejected by provider as invalid (bad schema, unsupported param). |
| Auth / config | `PROVIDER_AUTH_ERROR` | No | Invalid or missing API key, unauthorised project, disabled API. |
| Unknown error | `PROVIDER_ERROR` | Depends | Catch-all for unclassified provider failures. |

## error_code naming conventions

- UPPER_SNAKE_CASE strings.
- Prefix with `PROVIDER_` for provider-originated errors.
- Prefix with `REQUEST_` for request-validation errors (e.g. `REQUEST_TOO_LARGE`).
- Use `MISSING_PROVIDER_RESULT` when the provider response omits a requested
  record.

## Mapping HTTP / error categories to error_code

### Gemini provider (design target)

| Condition | Proposed `error_code` |
|---|---|
| HTTP 429 | `RATE_LIMITED` |
| HTTP 401 / 403 | `PROVIDER_AUTH_ERROR` |
| HTTP 400 with validation message | `VALIDATION_ERROR` |
| timeout | `TIMEOUT` |
| connection error | `TRANSIENT_NETWORK` |
| JSON parse failure | `MALFORMED_PROVIDER_RESPONSE` |
| empty response | `MALFORMED_PROVIDER_RESPONSE` |
| safety block / refuse | `PROVIDER_REFUSAL` |
| missing record_ids | `MISSING_PROVIDER_RESULT` |

### Mock provider

The mock provider never raises errors by design. All mock results have
`status="completed"` and `error_code=None`.

## Retry behavior

**Current implementation:** no retry logic exists.

**Design target:** the service should distinguish retryable from non-retryable
errors and apply exponential backoff with jitter for retryable categories.
See [SUMMARY_JOB_LIFECYCLE.md](SUMMARY_JOB_LIFECYCLE.md) for lifecycle
implications.

## Error propagation

Provider errors are propagated through the pipeline as follows:

1. `ProviderError` (or subclass) raised by the provider.
2. Caught in `ParagraphSummaryService._process_batch()`.
3. All records in the failing batch are marked `failed` with `error_code` set to
   the exception's `error_code`.
4. Processing continues to the next batch.
5. The response returns aggregated counts of `records_failed` alongside
   `records_completed`.

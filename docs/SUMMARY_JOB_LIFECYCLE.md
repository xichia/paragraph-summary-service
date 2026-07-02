# Summary Job Lifecycle (Design)

This document defines the lifecycle semantics for a paragraph-summary job—a single
`POST /paragraph-summaries` request that produces one JSONL sidecar artifact.

**Status: design documentation.** The current implementation (`v0.1.x`) processes
all records synchronously in a single request and does not implement queueing,
async workers, or lifecycle state machines. See
[Architecture](architecture.md) for the current synchronous pipeline.

## Lifecycle statuses

| Status | Terminal | Description |
|---|---|---|
| `queued` | No | Request accepted, pending processing. |
| `running` | No | Provider calls in progress for at least one batch. |
| `completed` | Yes | All records processed successfully. |
| `completed_with_errors` | Yes | Some records completed; others failed or skipped. |
| `failed` | Yes | All records failed; no usable artifact produced. |
| `skipped` | Yes | Record skipped (validation failure, unsupported doc type, pre-existing terminal state). |
| `cancelled` | Yes | Job cancelled before completion. |
| `retry_pending` | No | Some records failed with retryable errors; awaiting retry. |

### Non-terminal states

`queued`, `running`, and `retry_pending` are non-terminal. A job in these states
has not yet produced its final artifact.

### Terminal states

`completed`, `completed_with_errors`, `failed`, `skipped`, and `cancelled` are
terminal. A terminal job produces (or explicitly declines to produce) a final
JSONL artifact.

## Partial success (`completed_with_errors`)

A job reaches `completed_with_errors` when at least one record completes and at
least one record does not. The artifact includes every attempted record with its
individual status.

The response includes counts for all outcome categories:

- `records_completed`
- `records_failed`
- `records_skipped`
- `records_cancelled`

## Failed records

A record is marked `failed` when the provider returns an error for that record's
batch or the provider does not return a result for that record. The record's
`error_code` conveys the failure category (see
[PROVIDER_ERROR_SEMANTICS.md](PROVIDER_ERROR_SEMANTICS.md)).

Current implemented behavior (`v0.1.x`): when a batch raises `ProviderError`,
all records in that batch are marked `failed` with the exception's
`error_code`. Records missing from the provider response are marked `failed`
with `MISSING_PROVIDER_RESULT`.

## Skipped records

A record is `skipped` when the service determines before any provider call that
the record cannot be processed—for example, empty text after redaction, or an
unsupported document type. Skipped records do not count toward provider costs.

Current implementation: skipped records are not yet explicitly tracked;
validation rejects the entire request rather than individual records.

## Cancellation

Cancellation stops processing and produces whatever results were obtained before
cancellation. Records not yet processed are marked `cancelled` in the artifact.

Current implementation: cancellation is not implemented. Processing is
synchronous and uninterruptible within a single request.

## Retry attempts (`retry_pending`)

Some provider errors are transient. A job enters `retry_pending` when one or
more records failed with a retryable error code and the service intends to retry
them.

Retry strategy (design target):

- Retryable errors: rate limit, timeout, transient network.
- Non-retryable errors: auth failure, validation error, provider refusal.
- Backoff: exponential with jitter, configurable max attempts.
- Per-batch granularity: if a batch fails with a retryable error, the entire
  batch may be retried.

Current implementation: no retry logic exists. A failing batch is immediately
marked failed and processing continues to the next batch.

## Recovery / import thinking

If the summary service goes down during processing, DeepReader should retry the
entire request. The cache ensures previously completed records are not
re-processed on retry.

In a future async/queue architecture, the service could:

- Track per-record retry count and rate-limit wait time.
- Support explicit retry endpoints for failed records.
- Export job-level telemetry (attempt count, wall-clock duration, per-batch
  latency).

Current implementation: recovery is fully the caller's responsibility. No
server-side retry queue exists.

# Server-side timestamp handling

## Responsible file

`src/services/enrichment.ts` — the `EnrichmentService.enrich()` method.

## The exact rule

The server does **not** mutate or overwrite the value the client sent. Instead, enrichment splits time into two distinct fields on the stored event:

- **`clientTimestamp`** — the client-supplied value, preserved verbatim: `clientTimestamp: raw.timestamp ?? null` (null if the client omitted it).
- **`serverTimestamp`** — an authoritative, server-assigned receive time: `const serverTimestamp = meta.receivedAt ?? Date.now();`

The governing invariant (documented in the class doc comment, `enrichment.ts` lines 31–39):

> The SERVER timestamp is authoritative. Whatever the client put in `timestamp` is preserved as `clientTimestamp` for drift analysis, but `serverTimestamp` (the receive time) is what every query and time-bucket uses. This prevents clients with bad clocks from skewing aggregates or back-dating events outside the current window.

So the precise rule applied to a client timestamp is: **keep it untouched as `clientTimestamp`, but ignore it for all querying/bucketing; the server stamps its own receive time as `serverTimestamp` and that is what queries and time buckets use.**

## What the customer is actually seeing

The customer's events are not being mutated — their original timestamp is retained in `clientTimestamp`. What they observe as "changed" is that the analytics views, aggregates, and time buckets are keyed on `serverTimestamp` (server receive time), not on the timestamp they sent. So an event back-dated (or future-dated) by the client still lands in the bucket corresponding to when the server received it.

## Supporting / related files

- `src/services/ingestion.ts` — orchestrates the pipeline (validate → enrich → persist). `IngestionService.ingest()` returns `serverTimestamp` to the caller as the authoritative time. Enrichment is invoked at `ingestion.ts:47`.
- `src/lib/validate.ts` — `validateRawEvent()` only *validates* the client timestamp; it never reassigns it. It rejects (HTTP 400, does not silently change) timestamps that are:
  - more than `MAX_FUTURE_SKEW_MS` = 5 minutes in the future, or
  - older than `MAX_PAST_AGE_MS` = 30 days in the past.

  Its doc comment explicitly notes it "does NOT assign the server timestamp or any derived fields — that happens later in the enrichment step."

## Bottom line

`src/services/enrichment.ts` is the responsible file. The rule: the client's timestamp is preserved (as `clientTimestamp`) and never overwritten, but the server assigns its own receive time (`serverTimestamp = meta.receivedAt ?? Date.now()`) and that server timestamp — not the client's — is authoritative for every query and time-bucket. Validation in `lib/validate.ts` separately rejects client timestamps more than 5 minutes in the future or more than 30 days old.

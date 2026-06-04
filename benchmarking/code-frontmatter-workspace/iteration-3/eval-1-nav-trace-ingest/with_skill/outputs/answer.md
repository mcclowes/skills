# Trace: `POST /v1/events`

## Files involved, in order

1. **`src/server.ts`** — composition root. Mounts middleware in order, then the ingest router. Requests pass through the middleware chain first.
2. **`src/middleware/requestLog.ts`** — logs the request (assigns/echoes `requestId`).
3. **`src/middleware/auth.ts`** — API-key auth wall. Reads `X-API-Key` / `Authorization: Bearer`, looks the key up in `config.apiKeys`, and sets `req.auth.apiKeyId` (401 missing / 403 unknown).
4. **`src/middleware/rateLimit.ts`** — per-key token bucket on `req.auth.apiKeyId` (429 + Retry-After if empty).
5. **`src/routes/ingest.ts`** — the `POST /v1/events` handler. Thin: builds `RequestMeta` (IP via `X-Forwarded-For`, user-agent, `apiKeyId`) and delegates to the ingestion service; maps errors to status codes.
6. **`src/services/ingestion.ts`** — write-path orchestrator: `validate → enrich → persist`.
7. **`src/lib/validate.ts`** — validation step.
8. **`src/services/enrichment.ts`** — enrichment step (derived fields + authoritative server timestamp); calls `src/lib/useragent.ts`.
9. **`src/store/store.ts`** — `EventStore` interface / domain types.
10. **`src/store/store-postgres.ts`** (or `store-clickhouse.ts` / `store-memory.ts`, per `config.storageBackend`) — the concrete store that performs the write.

## Where the event is validated

`src/services/ingestion.ts:56` — `ingest()` calls `validateRawEvent(body)`.

That runs **`src/lib/validate.ts`** (`validateRawEvent`), which turns the untrusted body into a `RawEvent` or throws `ValidationError` (field + code). It checks the event type against `EVENT_TYPES`, clock-skew, `userId` length, and properties size. The handler in `routes/ingest.ts` catches `ValidationError` and maps it to a structured **400**.

Note: the timestamp check in `validate.ts` is sanity-only — the authoritative server timestamp is assigned later in `enrichment.ts`.

## Where the event is written to storage

`src/services/ingestion.ts:58` — `ingest()` calls `await this.store.insert(event)`.

This persists the enriched `Event` through the **`EventStore.insert`** contract (`src/store/store.ts`), implemented by the configured backend — by default **`src/store/store-postgres.ts`** (single-row INSERT into the `events` table). The backend is selected once at startup in `server.ts` from `config.storageBackend`.

(The `/v1/events/batch` sibling uses `validateRawEvent` per item then `store.insertBatch`, allowing partial success.)

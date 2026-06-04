# Trace: `POST /v1/events`

## Files involved, in order

1. **`src/server.ts`** — `buildApp` wires everything up. The request passes through global middleware first: `express.json` (256kb limit), `requestLogger`, `healthRouter` (skipped), then `apiKeyAuth` and `rateLimit` (the auth + rate-limit wall), before reaching the ingest router.
2. **`src/routes/ingest.ts`** — the `POST /v1/events` handler. It builds `RequestMeta` from the connection (IP from `X-Forwarded-For` / socket, user-agent header, `apiKeyId` from `req.auth`) via `requestMeta`, then delegates to `ingestion.ingest(req.body, meta)`. On success returns `202` with `{ eventId, serverTimestamp }`; `handleIngestError` maps a `ValidationError` to `400` and anything else to `500`.
3. **`src/services/ingestion.ts`** — `IngestionService.ingest` runs the pipeline: validate → enrich → persist.
4. **`src/lib/validate.ts`** — `validateRawEvent` (called from `ingest`).
5. **`src/services/enrichment.ts`** — `EnrichmentService.enrich` builds the storable `Event`.
6. **`src/store/store.ts`** — the `EventStore` interface (`insert`).
7. **`src/store/store-postgres.ts`** — default concrete backend; `insert` → `insertBatch` does the actual write. (Backend is selected by `createEventStore` in `server.ts` from `config.storageBackend`, default `postgres`; alternatives are `store-clickhouse.ts` / `store-memory.ts`.)

## Where the event is validated

`src/services/ingestion.ts:46`, the first line of `ingest`:

```ts
const raw = validateRawEvent(body);
```

The actual checks live in **`src/lib/validate.ts`**, `validateRawEvent` (line 58): body must be a plain object; `type` must be one of the known `EVENT_TYPES`; `userId` required, non-empty, ≤256 chars; optional `timestamp` must be finite and within the future-skew / 30-day-past window; optional `properties` ≤32 KiB; optional `context.url`/`context.referrer`. It throws `ValidationError` (with `field` + `code`) on the first problem, which the route turns into a `400`.

## Where the event is written to storage

`src/services/ingestion.ts:48`, after enrichment:

```ts
const event = this.enrichment.enrich(raw, meta);
await this.store.insert(event);
```

`enrich` (`src/services/enrichment.ts:43`) assigns the authoritative `id`, `serverTimestamp`, geo, parsed user-agent, etc. The write itself is `EventStore.insert`, which on the default backend is **`src/store/store-postgres.ts:43`** (`insert` delegates to `insertBatch`, the real DB write).

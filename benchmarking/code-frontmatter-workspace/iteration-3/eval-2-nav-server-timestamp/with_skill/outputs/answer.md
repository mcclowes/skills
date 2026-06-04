# Server-side timestamp rewriting

## Responsible file

`src/services/enrichment.ts` — the `EnrichmentService.enrich()` method.

This is the single place where a validated `RawEvent` becomes a storable `Event` and where the server-side timestamp is assigned.

## The exact rule applied to client timestamps

The server treats its own receive time as **authoritative** and never uses the client's timestamp as the event's effective time:

- On enrichment, the server computes `serverTimestamp = meta.receivedAt ?? Date.now()` — i.e. the moment the server received the request (`Date.now()`, or an injected `receivedAt` used for deterministic tests).
- The client-supplied `timestamp` is **not discarded but also not used as the event time**. It is preserved verbatim on the stored event as `clientTimestamp` (`clientTimestamp: raw.timestamp ?? null`), kept only for drift/clock-skew analysis.
- Every query, aggregation, and time-bucket operation uses `serverTimestamp`, never `clientTimestamp`. So from the customer's perspective, the timestamp they send appears to be "changed" because it is recorded separately and the server's receive time is what shows up in results.

Stated as the invariant from the code:

> The server timestamp is authoritative. Whatever the client put in `timestamp` is preserved as `clientTimestamp` for drift analysis, but `serverTimestamp` (the receive time) is what every query and time-bucket uses. This prevents clients with bad clocks from skewing aggregates or back-dating events outside the current window.

Relevant lines (`src/services/enrichment.ts`):

```ts
enrich(raw: RawEvent, meta: RequestMeta): Event {
  const serverTimestamp = meta.receivedAt ?? Date.now();

  return {
    id: randomUUID(),
    type: raw.type,
    userId: raw.userId,
    // Authoritative time wins over any client-supplied timestamp.
    serverTimestamp,
    clientTimestamp: raw.timestamp ?? null,
    ...
  };
}
```

## Note: where the client timestamp is *not* handled

`src/lib/validate.ts` also touches the client `timestamp`, but only as **sanity checks**, not the rewrite rule. It rejects values that are non-finite, more than 5 minutes in the future (`MAX_FUTURE_SKEW_MS`), or older than the 30-day retention window (`MAX_PAST_AGE_MS`). It does **not** assign or overwrite the timestamp — that happens exclusively in `enrichment.ts`. So if a customer's accepted timestamp is being "changed," the cause is the authoritative-server-timestamp rule in `enrichment.ts`, not validation.

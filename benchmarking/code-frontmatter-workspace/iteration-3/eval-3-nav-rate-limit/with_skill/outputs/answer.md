# Rate limiting in analytics-api

Rate limiting is applied **per-API-key**, not globally.

It is implemented in `src/middleware/rateLimit.ts`, a per-API-key token-bucket limiter (lazy refill). It keys each bucket on `req.auth.apiKeyId` — the identifier set upstream by the auth middleware (`src/middleware/auth.ts`) — so each API key gets its own bucket. When a key's bucket is empty it returns `429` with a `Retry-After` header. It fails closed (`500`) if it somehow runs before auth.

Bucket size comes from `config.rateLimit` (`ratePerSecond`, `burst`) in `src/config.ts`. The limiter is mounted in `src/server.ts` after the auth wall, which also runs an `evictIdle` timer to bound memory.

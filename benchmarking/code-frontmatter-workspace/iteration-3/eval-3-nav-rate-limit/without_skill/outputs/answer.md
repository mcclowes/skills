# Rate limiting: per-API-key

Rate limiting is applied **per-API-key**, not globally.

- **Implementation file:** `src/middleware/rateLimit.ts`
- **How it works:** A `RateLimiter` class maintains an in-process token bucket per API key (`Map<string, Bucket>`). Each authenticated key gets its own bucket of depth `burst` that refills at `ratePerSecond`; a request costs one token, and an empty bucket yields a `429` with a `Retry-After` header. The Express adapter `rateLimit()` keys off `req.auth.apiKeyId`.
- **Wiring (`src/server.ts`):** `apiKeyAuth` runs first, then `rateLimit(limiter)`, so the limiter always has an API key to key on (it fails closed with a 500 if it ever runs before auth). There is a single shared `RateLimiter` instance, but isolation is per-key — callers sharing a key share a budget.

Note: the limiting is per-key but per-process (state lives in memory; a multi-instance deployment would need a shared store like Redis).

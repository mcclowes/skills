# Tracing a short-link visit

When a user visits a short link (`GET /:slug`), control flows through these files in order:

1. **`server.ts`** — HTTP entry point. The `handle()` function matches `GET` with a non-empty path, strips the leading `/` to get the `slug`, and calls `shortener.resolve(slug)`. On a hit it responds `302` redirect to the target URL; on a miss it returns `404`. (The `shortener` is wired to a `RedisStore` at startup.)

2. **`shortener.ts`** — `Shortener.resolve(slug)`:
   - calls `store.getBySlug(slug)`; returns `null` (→ 404) if not found,
   - calls `store.incrementClicks(slug)` as a side effect,
   - returns `record.target` for the redirect.

3. **`store-redis.ts`** — `RedisStore` (the runtime backend selected in `server.ts`):
   - `getBySlug()` reads the link record via `redis.hgetall`,
   - **`incrementClicks()` is where the click counter is incremented**, via `redis.hincrby(\`${prefix}${slug}\`, "clicks", 1)`.

## Where the click counter gets incremented

- **Logical trigger:** `Shortener.resolve()` in `shortener.ts` (line 52) calls `store.incrementClicks(slug)` after a successful lookup.
- **Actual increment:** `RedisStore.incrementClicks()` in `store-redis.ts` (lines 55–57), which runs `hincrby(..., "clicks", 1)` against Redis.

(`store.ts` defines the `LinkStore.incrementClicks` interface and an in-memory implementation, but `server.ts` wires up `RedisStore`, so the Redis version is what runs.)

Files involved, in order: `server.ts` → `shortener.ts` → `store-redis.ts` (implementing the `store.ts` interface).

Files I opened in full: server.ts, shortener.ts, store-redis.ts

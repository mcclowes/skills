# Trace: visiting a short link

When a user visits a short link (`GET /:slug`), control flows through these files in order:

1. **`src/server.ts`** — HTTP entry point. The `GET` branch in `handle()` extracts the slug from the URL (`req.url.slice(1)`) and calls `shortener.resolve(slug)`. On a hit it replies `302` with `Location: target`; on a miss it returns `404`.

2. **`src/shortener.ts`** — `Shortener.resolve(slug)`:
   - calls `store.getBySlug(slug)` to look up the link record; returns `null` if not found,
   - calls `store.incrementClicks(slug)` as a side effect,
   - returns `record.target`.

3. **`src/store-redis.ts`** — `RedisStore` (the backend wired up at startup in `server.ts` via `RedisStore.fromConfig(redisClient)`):
   - `getBySlug()` does `redis.hgetall("link:<slug>")`,
   - **`incrementClicks()` is where the counter is incremented** — `redis.hincrby("link:<slug>", "clicks", 1)`.

`src/store.ts` defines the `LinkStore` interface (and the `clicks` field on `LinkRecord`) that `RedisStore` implements.

## Where the click counter is incremented

The increment is triggered in `Shortener.resolve()` (`src/shortener.ts`, line 52) and physically performed in `RedisStore.incrementClicks()` (`src/store-redis.ts`, lines 55-57) via a Redis `HINCRBY` on the `clicks` field of the `link:<slug>` hash.

Note: the click is counted on every successful resolve, after the lookup succeeds, and is fire-and-forget within `resolve` (awaited but its result is discarded).

Files I opened in full: none — read frontmatter (lines 1-20) of all 7 source files, then read only the relevant code bodies of server.ts, shortener.ts, and store-redis.ts (codec.ts, validate.ts, config.ts, and store.ts were never read beyond their frontmatter/header).

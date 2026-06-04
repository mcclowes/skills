# Visiting a short link: trace

When a user visits a short link (`GET /:slug`), the request flows through these files in order:

1. **`server.ts`** — HTTP entry point. The `handle()` function matches `GET` requests with a path longer than `/`, strips the leading slash to get the `slug`, and calls `shortener.resolve(slug)`. If a target comes back it responds `302` with a `Location` header; otherwise `404`.

2. **`shortener.ts`** — `Shortener.resolve(slug)`. Looks up the record via `store.getBySlug(slug)`. If none, returns `null`. Otherwise it calls **`store.incrementClicks(slug)`** (the click side effect) and returns `record.target`.

3. **`store.ts` / `store-redis.ts`** — the storage backend behind the `LinkStore` interface. The server wires up `RedisStore` at startup (`RedisStore.fromConfig(redisClient)`), so in production:
   - `getBySlug(slug)` reads the hash `link:<slug>` via `hgetall`.
   - `incrementClicks(slug)` runs `hincrby("link:<slug>", "clicks", 1)`.

   (The in-memory implementation in `store.ts` does the equivalent `rec.clicks += 1`.)

## Where the click counter is incremented

In **`shortener.ts`**, `resolve()` calls `store.incrementClicks(slug)`. The actual increment happens in the store implementation — for production that's `RedisStore.incrementClicks` in **`store-redis.ts`** (`hincrby` on the `clicks` field); the in-memory equivalent is `InMemoryStore.incrementClicks` in **`store.ts`**.

## Call order

`server.ts handle()` → `Shortener.resolve()` (shortener.ts) → `store.getBySlug()` → `store.incrementClicks()` (store-redis.ts in production) → `302` redirect to the target.

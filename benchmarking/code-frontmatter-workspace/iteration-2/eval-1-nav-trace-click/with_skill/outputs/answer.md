# Visiting a short link: request trace

When a user visits a short link (`GET /:slug`), four files are involved, in this order:

1. **`server.ts`** — HTTP entry point. The request matches the `GET` branch, the leading `/` is stripped to get the `slug`, and it calls `shortener.resolve(slug)`. On a hit it responds `302` with a `Location` header pointing at the target; on a miss, `404`.

2. **`shortener.ts`** — `Shortener.resolve(slug)`. Looks the record up via `store.getBySlug(slug)`. If nothing is found it returns `null` (no click counted). Otherwise it calls `store.incrementClicks(slug)`, then returns `record.target`.

3. **`store.ts`** — defines the `LinkStore` interface (`getBySlug`, `incrementClicks`, etc.) that `resolve` programs against.

4. **`store-redis.ts`** — the production `LinkStore` implementation wired up in `server.ts`. `getBySlug` reads the hash via `hgetall`; `incrementClicks` does the actual mutation.

## Where the click counter is incremented

The counter is bumped in **`shortener.ts`**, inside `resolve()`, via the call to `store.incrementClicks(slug)` (only after a record is found).

The concrete write lives in **`store-redis.ts`**, in `incrementClicks()`:

```ts
await this.redis.hincrby(`${this.prefix}${slug}`, "clicks", 1);
```

So: `server.ts` (GET /:slug) → `shortener.resolve()` → `store.incrementClicks()` → `RedisStore.incrementClicks()` performs the `hincrby` on the `clicks` field.

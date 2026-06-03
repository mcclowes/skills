# Adding a Postgres storage backend

## 1. Model your implementation on
`src/store-redis.ts` — the existing `RedisStore` is the production reference implementation of a storage backend. Copy its structure to create `src/store-postgres.ts` (e.g. a `PostgresStore` class with a `fromConfig(...)` static factory).

## 2. Interface it must satisfy
`LinkStore`, defined in `src/store.ts`:

```ts
export interface LinkStore {
  nextId(): Promise<number>;
  save(record: LinkRecord): Promise<void>;
  getBySlug(slug: string): Promise<LinkRecord | null>;
  incrementClicks(slug: string): Promise<void>;
}
```

It persists `LinkRecord` objects (`{ id, slug, target, createdAt, clicks }`, also in `store.ts`). `src/store.ts` also contains `InMemoryStore` as a second example implementation.

## 3. File that wires the backend up at startup
`src/server.ts`. It is the HTTP entry point and selects/instantiates the concrete backend at startup:

```ts
const shortener = new Shortener(RedisStore.fromConfig(redisClient));
```

Swap that line to construct your `PostgresStore` instead. `Shortener` (`src/shortener.ts`) receives the store via its constructor (dependency injection) and is backend-agnostic, so it needs no changes. Connection config lives in `src/config.ts`.

Note: a comment in `store.ts` says to "wire it up in shortener.ts," but the actual startup wiring (the line that picks the concrete backend) is in `server.ts`.

Files I opened in full: none (read only frontmatter/relevant ranges of store.ts, store-redis.ts, server.ts, shortener.ts).

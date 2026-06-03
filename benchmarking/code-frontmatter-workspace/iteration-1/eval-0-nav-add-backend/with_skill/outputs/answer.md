# Adding a Postgres storage backend

## Model your implementation on
`src/store-redis.ts` — it is the existing alternate (non-in-memory) backend. Copy its shape into a new `src/store-postgres.ts`: a class `PostgresStore implements LinkStore`, taking the DB client via the constructor, with a `static fromConfig(...)` factory that reads connection settings from `config.ts`.

## Interface you must satisfy
`LinkStore`, defined in `src/store.ts`:

```ts
interface LinkStore {
  nextId(): Promise<number>;
  save(record: LinkRecord): Promise<void>;
  getBySlug(slug: string): Promise<LinkRecord | null>;
  incrementClicks(slug: string): Promise<void>;
}
```

where `LinkRecord` is `{ id, slug, target, createdAt, clicks }` (also in `store.ts`). `InMemoryStore` in the same file is a second reference implementation.

## Where the backend is wired up at startup
`src/server.ts` — line 19 constructs the service with the chosen backend:

```ts
const shortener = new Shortener(RedisStore.fromConfig(redisClient));
```

Swap `RedisStore.fromConfig(...)` for `PostgresStore.fromConfig(...)` (and its import on line 13) to switch backends.

Note: the doc comment in `store.ts` says "wire it up in shortener.ts", but the actual instantiation/selection happens in `server.ts`; `shortener.ts` only consumes whatever `LinkStore` it is handed.

Files I opened in full: src/store.ts, src/store-redis.ts

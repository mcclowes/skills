# Adding a Postgres storage backend

**Model your new file on:** `store-redis.ts`

It is the existing production backend implementation. It shows the exact pattern to copy: a class implementing the storage interface, plus a `static fromConfig(...)` factory that pulls connection details from `config.ts`. Create a sibling `store-postgres.ts` alongside it.

**Interface it must satisfy:** `LinkStore`, defined in `store.ts`.

```ts
export interface LinkStore {
  nextId(): Promise<number>;
  save(record: LinkRecord): Promise<void>;
  getBySlug(slug: string): Promise<LinkRecord | null>;
  incrementClicks(slug: string): Promise<void>;
}
```

`store.ts` is the storage seam; it also defines the `LinkRecord` type your `save`/`getBySlug` methods read and return. (`InMemoryStore` in the same file is a second reference implementation.)

**File that wires the backend up at startup:** `server.ts`

It is the HTTP entry point and constructs the backend on line 19:

```ts
const shortener = new Shortener(RedisStore.fromConfig(redisClient));
```

Swap that for your Postgres store (e.g. `PostgresStore.fromConfig(...)`) and update the import on line 13 to point at `store-postgres.ts`.

Note: the in-code comment in `store.ts` says to wire backends up in `shortener.ts`, but the actual wiring lives in `server.ts` — that is where the store is instantiated and passed into `Shortener`.

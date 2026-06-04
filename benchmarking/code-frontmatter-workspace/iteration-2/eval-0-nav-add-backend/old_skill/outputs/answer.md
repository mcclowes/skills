# Adding a Postgres storage backend

## Model your implementation on

`src/store-redis.ts` — the existing `RedisStore` class is the production backend and the closest template for a new `PostgresStore`. Copy its shape: a class implementing `LinkStore`, a `static fromConfig(...)` factory that pulls connection settings from `getConfig()`, and a constructor taking a client plus key/table prefix.

## Interface you must satisfy

`LinkStore`, defined in `src/store.ts`. Your `PostgresStore` must `implements LinkStore`, which requires these four async methods (operating on `LinkRecord`):

```ts
interface LinkStore {
  nextId(): Promise<number>;
  save(record: LinkRecord): Promise<void>;
  getBySlug(slug: string): Promise<LinkRecord | null>;
  incrementClicks(slug: string): Promise<void>;
}
```

`LinkRecord` (also in `store.ts`): `{ id: number; slug: string; target: string; createdAt: number; clicks: number }`.

## File that wires the backend up at startup

`src/server.ts`. It instantiates the concrete backend at module load:

```ts
const shortener = new Shortener(RedisStore.fromConfig(redisClient));
```

Swap `RedisStore` here for your `PostgresStore` (e.g. `new Shortener(PostgresStore.fromConfig(pgClient))`). `shortener.ts` only consumes the injected `LinkStore` and does not pick the backend, so no change is needed there beyond passing the new store in.

## Also worth touching

`src/config.ts` defines the `Config` interface and `getConfig()`; add a `databaseUrl` (and any prefix/table) field there so `PostgresStore.fromConfig` has connection settings to read, mirroring how `RedisStore` reads `redisUrl`/`redisKeyPrefix`.

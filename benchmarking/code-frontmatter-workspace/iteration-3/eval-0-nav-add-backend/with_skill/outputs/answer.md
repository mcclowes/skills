# Adding a DynamoDB storage backend

- **Interface to implement:** `src/store/store.ts` — defines the `EventStore` interface (the storage contract), the `RawEvent`/`Event`/`MetricResult` types, and `StorageError`. Your `DynamoDB` backend must implement `EventStore` and throw `StorageError`.
- **Best template to copy:** `src/store/store-postgres.ts` — the default/production backend. It implements `EventStore`, reads its connection config via `fromConfig()`, and pushes aggregation/bucketing down to the backend (using `buildBucketSeries`/`granularityMs` from `src/lib/time.ts`), which is the closest pattern to a real DynamoDB backend. (`store-clickhouse.ts` is an equally valid sibling template; `store-memory.ts` is simpler but does aggregation in JS rather than pushing it down.)
- **Backend selection / wiring at startup:** `src/server.ts` — the sole backend selector. It maps `config.storageBackend` to a concrete `EventStore` at boot, then wires the store, services, and middleware. Add the `dynamodb` case here.

Supporting change: `src/config.ts` is the only reader of env vars and defines the `Config` type (including the backend choice and per-backend connection settings like `postgresUrl`). Add your DynamoDB config field(s) there and the corresponding `storageBackend` value so `server.ts` can select it.

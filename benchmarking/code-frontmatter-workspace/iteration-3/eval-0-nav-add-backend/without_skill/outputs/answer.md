# Adding a DynamoDB storage backend

## Interface to implement

`src/store/store.ts`

Defines the `EventStore` interface (the storage contract) plus all shared types (`Event`, `RawEvent`, `TimeRange`, `CountQuery`, `DistinctUsersQuery`, `TimeBucket`, etc.) and the `StorageError` class. Your `DynamoDbEventStore` must implement `EventStore`: `insert`, `insertBatch`, `queryRange`, `countByType`, `distinctUsers`, and `close`.

## Best template to copy

`src/store/store-clickhouse.ts`

Copy this rather than the Postgres one. ClickHouse, like DynamoDB, talks to a remote service over a network client (HTTP `fetch`) rather than a `pg` connection pool, and its `close()` is a no-op for a stateless client — both closer to a typical DynamoDB SDK setup than the pooled Postgres store. It also shows the `static fromConfig()` pattern that reads `loadConfig()`, validates the required config value, and throws `StorageError` if it is missing. `store-postgres.ts` (the default backend) and `store-memory.ts` (no external service) are the other implementations for reference.

## Where the backend is selected/wired at startup

`src/server.ts`

`createEventStore(config)` is the single `switch` on `config.storageBackend` that maps the backend name to a concrete store (`PostgresEventStore` / `ClickHouseEventStore` / `InMemoryEventStore`). Add a `case "dynamodb": return DynamoDbEventStore.fromConfig();` and import the new class here. The `default` branch is an exhaustiveness guard (`const never: never = config.storageBackend`), so it will fail to compile until you also add the new value to the type.

## Also required (supporting change)

`src/config.ts`

The `StorageBackend` union type (`"postgres" | "clickhouse" | "memory"`) and the `parseBackend()` validator both live here, plus any new connection config field (e.g. a `dynamoTable` / endpoint, mirroring `clickhouseUrl`). Add `"dynamodb"` to the union and to `parseBackend`, and add/validate the new config field, or the `server.ts` exhaustiveness guard will not compile and `STORAGE_BACKEND=dynamodb` will be rejected at load time.

## Summary

| Role | File |
| --- | --- |
| Interface to implement | `src/store/store.ts` (`EventStore`) |
| Template to copy | `src/store/store-clickhouse.ts` |
| Backend selection/wiring at startup | `src/server.ts` (`createEventStore`) |
| Supporting config change | `src/config.ts` (`StorageBackend` union, `parseBackend`) |

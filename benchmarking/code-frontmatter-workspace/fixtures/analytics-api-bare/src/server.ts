import express, { type Express } from "express";
import { loadConfig, type Config } from "./config";
import type { EventStore } from "./store/store";
import { PostgresEventStore } from "./store/store-postgres";
import { ClickHouseEventStore } from "./store/store-clickhouse";
import { InMemoryEventStore } from "./store/store-memory";
import { EnrichmentService } from "./services/enrichment";
import { IngestionService } from "./services/ingestion";
import { AggregationService } from "./services/aggregation";
import { apiKeyAuth } from "./middleware/auth";
import { RateLimiter, rateLimit } from "./middleware/rateLimit";
import { requestLogger } from "./middleware/requestLog";
import { ingestRouter } from "./routes/ingest";
import { queryRouter } from "./routes/query";
import { healthRouter } from "./routes/health";

/**
 * The ONLY place that maps config.storageBackend to a concrete EventStore.
 * Everything else depends on the EventStore interface, so swapping backends is a
 * one-line config change with no code edits elsewhere.
 */
export function createEventStore(config: Config): EventStore {
  switch (config.storageBackend) {
    case "postgres":
      return PostgresEventStore.fromConfig();
    case "clickhouse":
      return ClickHouseEventStore.fromConfig();
    case "memory":
      return InMemoryEventStore.fromConfig();
    default: {
      // Exhaustiveness guard: a new backend must be wired in here.
      const never: never = config.storageBackend;
      throw new Error(`unhandled storage backend: ${String(never)}`);
    }
  }
}

export interface App {
  express: Express;
  store: EventStore;
  /** Tears down storage and any background timers. */
  shutdown(): Promise<void>;
}

/**
 * Build the wired-up application: construct the store, the services on top of
 * it, the middleware, and mount the routers in order. Pure construction — does
 * not bind a port (see `start`), so tests can drive `app.express` directly.
 */
export function buildApp(config: Config = loadConfig()): App {
  const store = createEventStore(config);

  const enrichment = new EnrichmentService();
  const ingestion = new IngestionService(store, enrichment);
  const aggregation = new AggregationService(store);
  const limiter = RateLimiter.fromConfig(config);

  const app = express();
  app.use(express.json({ limit: "256kb" }));
  app.use(requestLogger(config));

  // Health checks are unauthenticated and must come before the auth wall.
  app.use(healthRouter(store));

  // Everything past here requires a valid API key, then a rate-limit token.
  app.use(apiKeyAuth(config));
  app.use(rateLimit(limiter));

  app.use(ingestRouter(ingestion));
  app.use(queryRouter(aggregation));

  app.use((_req, res) => {
    res.status(404).json({
      error: { code: "not_found", message: "no such route" },
    });
  });

  // Periodically reclaim idle rate-limit buckets so memory stays bounded.
  const evictTimer = setInterval(() => limiter.evictIdle(15 * 60_000), 60_000);
  evictTimer.unref();

  return {
    express: app,
    store,
    async shutdown() {
      clearInterval(evictTimer);
      await store.close();
    },
  };
}

/** Build the app and start listening. Returns the live server handle. */
export async function start(config: Config = loadConfig()) {
  const app = buildApp(config);
  const server = app.express.listen(config.port, () => {
    process.stdout.write(
      JSON.stringify({
        ts: new Date().toISOString(),
        level: "info",
        msg: "listening",
        port: config.port,
        backend: config.storageBackend,
        env: config.env,
      }) + "\n",
    );
  });

  const stop = async () => {
    server.close();
    await app.shutdown();
    process.exit(0);
  };
  process.on("SIGTERM", stop);
  process.on("SIGINT", stop);

  return { server, app };
}

// Boot when run directly (not when imported by tests).
if (process.argv[1] && process.argv[1].endsWith("server.js")) {
  start().catch((err) => {
    process.stderr.write(`fatal: ${String(err)}\n`);
    process.exit(1);
  });
}

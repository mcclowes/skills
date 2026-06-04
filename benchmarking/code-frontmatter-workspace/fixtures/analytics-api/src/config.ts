/**
 * ---
 * purpose: Central memoised config loaded from process.env — the only reader of env vars; defines the Config type (backend choice, API keys, rate-limit knobs) consumed everywhere.
 * related:
 *   - ./server.ts - calls loadConfig() at boot and switches on config.storageBackend to pick a store
 *   - ./middleware/auth.ts - validates request keys against config.apiKeys (key -> keyId map built here)
 *   - ./middleware/rateLimit.ts - reads config.rateLimit (ratePerSecond, burst) to size token buckets
 *   - ./store/store-postgres.ts - reads config.postgresUrl via loadConfig() in fromConfig()
 *   - ./store/store-clickhouse.ts - reads config.clickhouseUrl/clickhouseDatabase via loadConfig()
 * ---
 *
 * Central, memoised configuration loaded from the process environment.
 *
 * Nothing else in the codebase reads `process.env` directly — call `loadConfig()`
 * (cached) and pass the result down. `resetConfigForTests()` clears the cache so
 * tests can re-load with a mutated environment.
 */

export type StorageBackend = "postgres" | "clickhouse" | "memory";

export interface Config {
  port: number;
  env: "development" | "production" | "test";
  storageBackend: StorageBackend;

  /** Connection string for the Postgres backend; required when selected. */
  postgresUrl: string | null;
  /** HTTP endpoint for the ClickHouse backend; required when selected. */
  clickhouseUrl: string | null;
  clickhouseDatabase: string;

  /** Valid API keys, mapped key -> stable keyId used for rate-limit buckets. */
  apiKeys: Map<string, string>;

  rateLimit: {
    /** Sustained requests per second per API key. */
    ratePerSecond: number;
    /** Bucket depth — the largest burst a key can spend at once. */
    burst: number;
  };

  logLevel: "debug" | "info" | "warn" | "error";
}

let cached: Config | null = null;

export function loadConfig(env: NodeJS.ProcessEnv = process.env): Config {
  if (cached) return cached;
  cached = buildConfig(env);
  return cached;
}

export function resetConfigForTests(): void {
  cached = null;
}

class ConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ConfigError";
  }
}

function buildConfig(env: NodeJS.ProcessEnv): Config {
  const storageBackend = parseBackend(env.STORAGE_BACKEND);
  const postgresUrl = env.PG_URL ?? env.DATABASE_URL ?? null;
  const clickhouseUrl = env.CLICKHOUSE_URL ?? null;

  if (storageBackend === "postgres" && !postgresUrl) {
    throw new ConfigError(
      "STORAGE_BACKEND=postgres requires PG_URL (or DATABASE_URL)",
    );
  }
  if (storageBackend === "clickhouse" && !clickhouseUrl) {
    throw new ConfigError("STORAGE_BACKEND=clickhouse requires CLICKHOUSE_URL");
  }

  const apiKeys = parseApiKeys(env.API_KEYS);
  if (apiKeys.size === 0 && env.NODE_ENV !== "test") {
    throw new ConfigError("API_KEYS must list at least one key");
  }

  return {
    port: parseIntEnv(env.PORT, 8080),
    env: parseNodeEnv(env.NODE_ENV),
    storageBackend,
    postgresUrl,
    clickhouseUrl,
    clickhouseDatabase: env.CLICKHOUSE_DB ?? "analytics",
    apiKeys,
    rateLimit: {
      ratePerSecond: parseIntEnv(env.RATE_LIMIT_RPS, 50),
      burst: parseIntEnv(env.RATE_LIMIT_BURST, 100),
    },
    logLevel: parseLogLevel(env.LOG_LEVEL),
  };
}

function parseBackend(raw: string | undefined): StorageBackend {
  const value = (raw ?? "postgres").toLowerCase();
  if (value === "postgres" || value === "clickhouse" || value === "memory") {
    return value;
  }
  throw new ConfigError(`unknown STORAGE_BACKEND "${raw}"`);
}

/**
 * API_KEYS is a comma-separated list of either bare keys or `keyId:key` pairs.
 * A bare key uses the key itself as its id. The id is what the rate limiter and
 * logs key on, so a rotated key with the same id shares its bucket.
 */
function parseApiKeys(raw: string | undefined): Map<string, string> {
  const out = new Map<string, string>();
  if (!raw) return out;
  for (const chunk of raw.split(",")) {
    const trimmed = chunk.trim();
    if (trimmed === "") continue;
    const sep = trimmed.indexOf(":");
    if (sep === -1) {
      out.set(trimmed, trimmed);
    } else {
      const id = trimmed.slice(0, sep);
      const key = trimmed.slice(sep + 1);
      out.set(key, id);
    }
  }
  return out;
}

function parseIntEnv(raw: string | undefined, fallback: number): number {
  if (raw === undefined) return fallback;
  const n = Number.parseInt(raw, 10);
  if (Number.isNaN(n)) throw new ConfigError(`expected integer, got "${raw}"`);
  return n;
}

function parseNodeEnv(raw: string | undefined): Config["env"] {
  if (raw === "production" || raw === "test") return raw;
  return "development";
}

function parseLogLevel(raw: string | undefined): Config["logLevel"] {
  if (raw === "debug" || raw === "warn" || raw === "error") return raw;
  return "info";
}

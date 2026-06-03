/**
 * ---
 * purpose: Loads and memoises app config (baseUrl, redis, port) from env vars.
 * related:
 *   - ./server.ts - reads port to start the listener
 *   - ./store-redis.ts - reads redisKeyPrefix
 *   - ./shortener.ts - reads baseUrl to build short URLs
 * outputs:
 *   - getConfig(): Config - memoised; resetConfig() clears it for tests
 * ---
 */
export interface Config {
  baseUrl: string;
  redisUrl: string;
  redisKeyPrefix: string;
  port: number;
}

let cached: Config | null = null;

export function getConfig(): Config {
  if (cached) return cached;
  cached = {
    baseUrl: process.env.BASE_URL ?? "http://localhost:3000",
    redisUrl: process.env.REDIS_URL ?? "redis://localhost:6379",
    redisKeyPrefix: process.env.REDIS_PREFIX ?? "link:",
    port: Number(process.env.PORT ?? 3000),
  };
  return cached;
}

/** Test helper: clear the memoised config so env changes take effect. */
export function resetConfig(): void {
  cached = null;
}

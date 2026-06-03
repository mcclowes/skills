/**
 * ---
 * purpose: Loads and caches runtime configuration (base URL, Redis connection) from environment variables
 * related:
 *   - ./store-redis.ts - reads redisUrl/redisKeyPrefix from here
 *   - ./shortener.ts - reads baseUrl to build full short links
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

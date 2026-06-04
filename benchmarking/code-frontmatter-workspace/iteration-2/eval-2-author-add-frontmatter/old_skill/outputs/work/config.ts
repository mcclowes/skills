/**
 * ---
 * purpose: Memoised app config loaded from env vars (base URL, Redis, port)
 * exports:
 *   - getConfig - returns cached Config
 *   - resetConfig - clears cache (test helper)
 * related:
 *   - ./server.ts - reads port
 *   - ./shortener.ts - reads baseUrl
 *   - ./store-redis.ts - reads redisKeyPrefix
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

/**
 * ---
 * purpose: Redis-backed LinkStore for production; persists links and click counts across restarts
 * related:
 *   - ./store.ts - the LinkStore interface this implements
 *   - ./config.ts - supplies the Redis connection URL
 * ---
 */

import type { LinkRecord, LinkStore } from "./store";
import { getConfig } from "./config";

// Minimal Redis client shape we depend on (kept abstract for the fixture).
interface RedisLike {
  incr(key: string): Promise<number>;
  hset(key: string, value: Record<string, string>): Promise<void>;
  hgetall(key: string): Promise<Record<string, string> | null>;
  hincrby(key: string, field: string, by: number): Promise<number>;
}

export class RedisStore implements LinkStore {
  constructor(private redis: RedisLike, private prefix = "link:") {}

  static fromConfig(redis: RedisLike): RedisStore {
    const { redisKeyPrefix } = getConfig();
    return new RedisStore(redis, redisKeyPrefix);
  }

  async nextId(): Promise<number> {
    return this.redis.incr(`${this.prefix}seq`);
  }

  async save(record: LinkRecord): Promise<void> {
    await this.redis.hset(`${this.prefix}${record.slug}`, {
      id: String(record.id),
      slug: record.slug,
      target: record.target,
      createdAt: String(record.createdAt),
      clicks: String(record.clicks),
    });
  }

  async getBySlug(slug: string): Promise<LinkRecord | null> {
    const raw = await this.redis.hgetall(`${this.prefix}${slug}`);
    if (!raw || !raw.slug) return null;
    return {
      id: Number(raw.id),
      slug: raw.slug,
      target: raw.target,
      createdAt: Number(raw.createdAt),
      clicks: Number(raw.clicks),
    };
  }

  async incrementClicks(slug: string): Promise<void> {
    await this.redis.hincrby(`${this.prefix}${slug}`, "clicks", 1);
  }
}

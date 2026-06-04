import type { NextFunction, Request, Response } from "express";
import type { Config } from "../config";

/**
 * One key's worth of token-bucket state. Tokens refill continuously at
 * `ratePerSecond`; `tokens` is recomputed lazily on each request from the time
 * since `last`, so there's no background timer.
 */
interface Bucket {
  tokens: number;
  last: number;
}

/**
 * In-process token-bucket rate limiter, keyed PER API KEY (not per IP).
 *
 * Each authenticated key gets its own bucket of depth `burst` that refills at
 * `ratePerSecond`. A request costs one token; when the bucket is empty the
 * request is rejected with 429 and a `Retry-After` header. Because the key is
 * the bucket identity, all callers sharing a key share a budget — and an
 * unauthenticated request never reaches here (auth runs first).
 *
 * State is per-process; a multi-instance deployment would back this with Redis.
 */
export class RateLimiter {
  private readonly buckets = new Map<string, Bucket>();

  constructor(
    private readonly ratePerSecond: number,
    private readonly burst: number,
    private readonly now: () => number = Date.now,
  ) {}

  static fromConfig(config: Config): RateLimiter {
    return new RateLimiter(
      config.rateLimit.ratePerSecond,
      config.rateLimit.burst,
    );
  }

  /**
   * Try to spend one token for `key`. Returns whether the request is allowed
   * plus, when denied, how many ms until one token is available again.
   */
  tryConsume(key: string): { allowed: boolean; retryAfterMs: number } {
    const now = this.now();
    const bucket = this.buckets.get(key) ?? { tokens: this.burst, last: now };

    const elapsedSec = (now - bucket.last) / 1000;
    bucket.tokens = Math.min(
      this.burst,
      bucket.tokens + elapsedSec * this.ratePerSecond,
    );
    bucket.last = now;

    if (bucket.tokens >= 1) {
      bucket.tokens -= 1;
      this.buckets.set(key, bucket);
      return { allowed: true, retryAfterMs: 0 };
    }

    this.buckets.set(key, bucket);
    const deficit = 1 - bucket.tokens;
    return {
      allowed: false,
      retryAfterMs: Math.ceil((deficit / this.ratePerSecond) * 1000),
    };
  }

  /** Drop buckets untouched for a while so memory doesn't grow unbounded. */
  evictIdle(maxIdleMs: number): void {
    const cutoff = this.now() - maxIdleMs;
    for (const [key, bucket] of this.buckets) {
      if (bucket.last < cutoff) this.buckets.delete(key);
    }
  }
}

/**
 * Express adapter. Must run AFTER apiKeyAuth so `req.auth.apiKeyId` is set; if
 * it somehow isn't, we fail closed with a 500 rather than sharing one anonymous
 * bucket across every caller.
 */
export function rateLimit(limiter: RateLimiter) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const key = req.auth?.apiKeyId;
    if (!key) {
      res.status(500).json({
        error: {
          code: "rate_limit_misconfigured",
          message: "rate limiter ran before authentication",
        },
      });
      return;
    }

    const { allowed, retryAfterMs } = limiter.tryConsume(key);
    if (!allowed) {
      res.setHeader("Retry-After", Math.ceil(retryAfterMs / 1000).toString());
      res.status(429).json({
        error: {
          code: "rate_limited",
          message: "rate limit exceeded for API key",
          retryAfterMs,
        },
      });
      return;
    }

    next();
  };
}

/**
 * ---
 * purpose: Core service - validates a target, allocates an ID/slug, and resolves slugs
 * inputs:
 *   - store: LinkStore - storage backend (injected)
 * outputs:
 *   - ShortLink - { slug, shortUrl, target } from shorten()
 *   - string | null - target URL from resolve() (also increments click count)
 * related:
 *   - ./store.ts - LinkStore interface and LinkRecord
 *   - ./validate.ts - target URL validation
 *   - ./codec.ts - ID -> slug encoding
 *   - ./config.ts - baseUrl for shortUrl
 * ---
 */
import { encode } from "./codec";
import type { LinkStore } from "./store";
import { validateTarget } from "./validate";
import { getConfig } from "./config";

export interface ShortLink {
  slug: string;
  shortUrl: string;
  target: string;
}

export class Shortener {
  constructor(private store: LinkStore) {}

  async shorten(target: string): Promise<ShortLink> {
    const result = validateTarget(target);
    if (!result.ok || !result.normalised) {
      throw new Error(`invalid target: ${result.reason}`);
    }
    const id = await this.store.nextId();
    const slug = encode(id);
    await this.store.save({
      id,
      slug,
      target: result.normalised,
      createdAt: Date.now(),
      clicks: 0,
    });
    return { slug, shortUrl: `${getConfig().baseUrl}/${slug}`, target: result.normalised };
  }

  /** Resolve a slug to its target, counting the click as a side effect. */
  async resolve(slug: string): Promise<string | null> {
    const record = await this.store.getBySlug(slug);
    if (!record) return null;
    await this.store.incrementClicks(slug);
    return record.target;
  }
}

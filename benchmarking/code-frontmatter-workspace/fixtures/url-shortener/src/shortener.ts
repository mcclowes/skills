/**
 * ---
 * purpose: Core service tying validation, codec, and storage together to create and resolve short links
 * inputs:
 *   - store: LinkStore - storage backend (in-memory or Redis)
 *   - target: string - the URL to shorten
 * outputs:
 *   - ShortLink - slug plus the full short URL
 * related:
 *   - ./codec.ts - encodes the sequence ID into a slug
 *   - ./store.ts - persists and resolves LinkRecords
 *   - ./validate.ts - guards the target URL before shortening
 *   - ./config.ts - supplies baseUrl for building the full link
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

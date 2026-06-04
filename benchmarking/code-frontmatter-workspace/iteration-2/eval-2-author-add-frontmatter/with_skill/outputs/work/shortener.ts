/**
 * ---
 * purpose: Core service - validates a target, mints a slug, saves it, and resolves slugs to targets.
 * related:
 *   - ./store.ts - LinkStore interface it persists through
 *   - ./codec.ts - turns the numeric id into a base62 slug
 *   - ./validate.ts - URL validation/SSRF guard applied before saving
 *   - ./config.ts - baseUrl used to build the returned short URL
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

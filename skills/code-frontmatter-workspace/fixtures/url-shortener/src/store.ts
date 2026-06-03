/**
 * ---
 * purpose: LinkStore interface plus an in-memory implementation; the seam for swapping storage backends
 * related:
 *   - ./store-redis.ts - production Redis-backed implementation of LinkStore
 *   - ./shortener.ts - consumes a LinkStore to persist and resolve links
 * ---
 */

export interface LinkRecord {
  id: number;
  slug: string;
  target: string;
  createdAt: number;
  clicks: number;
}

/**
 * Any storage backend must implement this interface. To add a new backend
 * (Postgres, DynamoDB, ...), implement LinkStore and wire it up in shortener.ts.
 */
export interface LinkStore {
  nextId(): Promise<number>;
  save(record: LinkRecord): Promise<void>;
  getBySlug(slug: string): Promise<LinkRecord | null>;
  incrementClicks(slug: string): Promise<void>;
}

export class InMemoryStore implements LinkStore {
  private seq = 0;
  private bySlug = new Map<string, LinkRecord>();

  async nextId(): Promise<number> {
    return ++this.seq;
  }

  async save(record: LinkRecord): Promise<void> {
    this.bySlug.set(record.slug, record);
  }

  async getBySlug(slug: string): Promise<LinkRecord | null> {
    return this.bySlug.get(slug) ?? null;
  }

  async incrementClicks(slug: string): Promise<void> {
    const rec = this.bySlug.get(slug);
    if (rec) rec.clicks += 1;
  }
}

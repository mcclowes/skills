/**
 * ---
 * purpose: Storage abstraction - LinkRecord shape, LinkStore interface, and an in-memory backend
 * exports:
 *   - LinkRecord - stored link fields
 *   - LinkStore - backend interface (implement to add Postgres/Dynamo/etc.)
 *   - InMemoryStore - non-persistent backend for tests/dev
 * related:
 *   - ./store-redis.ts - production Redis implementation
 *   - ./shortener.ts - consumes a LinkStore
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

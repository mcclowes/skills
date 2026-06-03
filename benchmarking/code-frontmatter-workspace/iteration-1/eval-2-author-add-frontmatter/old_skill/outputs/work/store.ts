/**
 * ---
 * purpose: Storage contract for links - LinkRecord type, LinkStore interface, InMemoryStore
 * outputs:
 *   - LinkRecord - stored link shape
 *   - LinkStore - interface every backend implements
 *   - InMemoryStore - Map-based backend for tests
 * related:
 *   - ./store-redis.ts - production LinkStore implementation
 *   - ./shortener.ts - consumes LinkStore
 * note: add a new backend by implementing LinkStore and wiring it in server.ts
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

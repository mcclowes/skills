import {
  type CountQuery,
  type DistinctUsersQuery,
  type Event,
  type EventStore,
  type EventType,
  type TimeBucket,
  type TimeRange,
} from "./store";
import { buildBucketSeries, floorTo, isWithin } from "../lib/time";

/**
 * ---
 * purpose: In-memory EventStore for tests and local dev — events in a plain array sorted lazily on read; aggregation done in JS rather than pushed down. Not durable. Selected via STORAGE_BACKEND=memory.
 * related:
 *   - ./store.ts - implements the EventStore interface
 *   - ../lib/time.ts - floorTo/isWithin/buildBucketSeries do the in-JS bucketing the SQL backends push down
 *   - ./store-postgres.ts - the durable default backend with identical behaviour
 * ---
 *
 * In-memory EventStore used by tests and local development. Keeps everything in
 * a plain array, sorted lazily on read. Not durable, not concurrent-safe across
 * processes — fine for a single Node process. Selected via STORAGE_BACKEND=memory.
 */
export class InMemoryEventStore implements EventStore {
  private events: Event[] = [];
  private dirty = false;

  static fromConfig(): InMemoryEventStore {
    // No connection to establish; signature mirrors the other backends so
    // server.ts can construct any store the same way.
    return new InMemoryEventStore();
  }

  async insert(event: Event): Promise<void> {
    this.events.push(event);
    this.dirty = true;
  }

  async insertBatch(events: Event[]): Promise<void> {
    if (events.length === 0) return;
    this.events.push(...events);
    this.dirty = true;
  }

  async queryRange(range: TimeRange, type?: EventType): Promise<Event[]> {
    this.ensureSorted();
    return this.events.filter(
      (e) =>
        isWithin(e.serverTimestamp, range) &&
        (type === undefined || e.type === type),
    );
  }

  async countByType(query: CountQuery): Promise<TimeBucket[]> {
    const matching = await this.queryRange(query.range, query.type);
    if (!query.granularity) {
      return [{ bucketStart: query.range.from, count: matching.length }];
    }
    const counts = new Map<number, number>();
    for (const e of matching) {
      const bucket = floorTo(e.serverTimestamp, query.granularity);
      counts.set(bucket, (counts.get(bucket) ?? 0) + 1);
    }
    return buildBucketSeries(query.range, query.granularity, counts);
  }

  async distinctUsers(query: DistinctUsersQuery): Promise<number> {
    const matching = await this.queryRange(query.range, query.type);
    const seen = new Set<string>();
    for (const e of matching) seen.add(e.userId);
    return seen.size;
  }

  async close(): Promise<void> {
    this.events = [];
    this.dirty = false;
  }

  /** Test helper: total stored events, ignoring time. */
  size(): number {
    return this.events.length;
  }

  private ensureSorted(): void {
    if (!this.dirty) return;
    this.events.sort((a, b) => a.serverTimestamp - b.serverTimestamp);
    this.dirty = false;
  }
}

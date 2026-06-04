/**
 * Storage seam for the analytics API.
 *
 * Everything below the service layer talks to events through the EventStore
 * interface. Concrete backends (Postgres, ClickHouse, in-memory) live in the
 * sibling store-*.ts files and are selected at startup in server.ts.
 */

export type EventType =
  | "page_view"
  | "click"
  | "purchase"
  | "signup"
  | "custom";

export const EVENT_TYPES: readonly EventType[] = [
  "page_view",
  "click",
  "purchase",
  "signup",
  "custom",
];

/**
 * A raw event as it arrives over the wire, before enrichment. Clients are
 * trusted for `type`, `userId` and `properties` but NOT for timing or network
 * metadata — those get overwritten during enrichment.
 */
export interface RawEvent {
  type: EventType;
  userId: string;
  /** Client-supplied epoch millis. Advisory only; the server timestamp wins. */
  timestamp?: number;
  properties?: Record<string, unknown>;
  /** Optional client-declared page/url context. */
  context?: {
    url?: string;
    referrer?: string;
  };
}

/**
 * A fully enriched, storable event. This is the shape that hits EventStore.insert.
 * `serverTimestamp` is authoritative; `clientTimestamp` is retained for drift
 * analysis but never used for bucketing.
 */
export interface Event {
  id: string;
  type: EventType;
  userId: string;
  /** Authoritative event time, assigned by the server during enrichment. */
  serverTimestamp: number;
  /** Whatever the client claimed, or null if it claimed nothing. */
  clientTimestamp: number | null;
  properties: Record<string, unknown>;
  /** Source IP captured at ingest, used for geo enrichment. */
  ip: string | null;
  geo: GeoInfo | null;
  userAgent: UserAgentInfo | null;
  apiKeyId: string;
}

export interface GeoInfo {
  country: string | null;
  region: string | null;
  city: string | null;
}

export interface UserAgentInfo {
  browser: string;
  os: string;
  device: "mobile" | "tablet" | "desktop" | "bot" | "unknown";
  raw: string;
}

/** Inclusive-start, exclusive-end time window, both in epoch millis. */
export interface TimeRange {
  from: number;
  to: number;
}

export type BucketGranularity = "hour" | "day";

/** One row of a bucketed time series. */
export interface TimeBucket {
  /** Bucket start, epoch millis, floored to the granularity. */
  bucketStart: number;
  count: number;
}

/** Generic shape returned by aggregation queries. */
export interface MetricResult {
  metric: string;
  range: TimeRange;
  value: number;
  buckets?: TimeBucket[];
}

export interface CountQuery {
  range: TimeRange;
  type?: EventType;
  granularity?: BucketGranularity;
}

export interface DistinctUsersQuery {
  range: TimeRange;
  type?: EventType;
}

/**
 * The storage contract. Implemented by PostgresEventStore (default),
 * ClickHouseEventStore and InMemoryEventStore.
 */
export interface EventStore {
  /** Persist a single enriched event. */
  insert(event: Event): Promise<void>;

  /** Persist a batch; default implementations may loop over insert. */
  insertBatch(events: Event[]): Promise<void>;

  /** Return raw events whose serverTimestamp falls inside the range. */
  queryRange(range: TimeRange, type?: EventType): Promise<Event[]>;

  /** Count events in range, optionally bucketed by hour/day. */
  countByType(query: CountQuery): Promise<TimeBucket[]>;

  /** Number of distinct userIds in range. */
  distinctUsers(query: DistinctUsersQuery): Promise<number>;

  /** Release pooled connections, flush buffers, etc. */
  close(): Promise<void>;
}

/** Thrown by stores when the underlying backend is unreachable or errors. */
export class StorageError extends Error {
  constructor(
    message: string,
    readonly cause?: unknown,
  ) {
    super(message);
    this.name = "StorageError";
  }
}

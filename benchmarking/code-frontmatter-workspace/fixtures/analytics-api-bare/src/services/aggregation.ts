import {
  type BucketGranularity,
  type EventStore,
  type EventType,
  type MetricResult,
  type TimeRange,
} from "../store/store";

export interface CountParams {
  range: TimeRange;
  type?: EventType;
  granularity?: BucketGranularity;
}

export interface UniqueUsersParams {
  range: TimeRange;
  type?: EventType;
}

export interface TopEventTypesParams {
  range: TimeRange;
  limit?: number;
}

export interface TopEventType {
  type: EventType;
  count: number;
}

/**
 * Read-side service. Translates the query routes' parameters into EventStore
 * calls and assembles MetricResults. It holds no storage logic of its own — the
 * heavy lifting (bucketing, distinct counts) is pushed down to the store so it
 * runs in the database for the SQL/columnar backends.
 */
export class AggregationService {
  constructor(private readonly store: EventStore) {}

  /**
   * Total event count over a range, optionally filtered by type and broken into
   * hour/day buckets. When `granularity` is set the result carries a dense,
   * zero-filled `buckets` array; the scalar `value` is the sum across buckets.
   */
  async count(params: CountParams): Promise<MetricResult> {
    const buckets = await this.store.countByType({
      range: params.range,
      type: params.type,
      granularity: params.granularity,
    });
    const value = buckets.reduce((sum, b) => sum + b.count, 0);
    return {
      metric: params.type ? `count:${params.type}` : "count",
      range: params.range,
      value,
      buckets: params.granularity ? buckets : undefined,
    };
  }

  /** Distinct userId count over a range, optionally filtered by event type. */
  async uniqueUsers(params: UniqueUsersParams): Promise<MetricResult> {
    const value = await this.store.distinctUsers({
      range: params.range,
      type: params.type,
    });
    return {
      metric: params.type ? `unique_users:${params.type}` : "unique_users",
      range: params.range,
      value,
    };
  }

  /**
   * Leaderboard of event types by volume. There's no dedicated store method for
   * this, so we fan out one count per known type and sort. Cheap because each
   * count is a pushed-down aggregate, not a row scan.
   */
  async topEventTypes(params: TopEventTypesParams): Promise<TopEventType[]> {
    const limit = params.limit ?? 10;
    const types: EventType[] = [
      "page_view",
      "click",
      "purchase",
      "signup",
      "custom",
    ];

    const counts = await Promise.all(
      types.map(async (type) => {
        const buckets = await this.store.countByType({
          range: params.range,
          type,
        });
        const count = buckets.reduce((sum, b) => sum + b.count, 0);
        return { type, count };
      }),
    );

    return counts
      .filter((c) => c.count > 0)
      .sort((a, b) => b.count - a.count)
      .slice(0, limit);
  }
}

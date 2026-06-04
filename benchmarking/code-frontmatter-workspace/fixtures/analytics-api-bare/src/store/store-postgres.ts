import { Pool, type PoolClient } from "pg";
import { loadConfig } from "../config";
import {
  type CountQuery,
  type DistinctUsersQuery,
  type Event,
  type EventStore,
  type EventType,
  StorageError,
  type TimeBucket,
  type TimeRange,
} from "./store";
import { buildBucketSeries, granularityMs } from "../lib/time";

/**
 * Default/production EventStore, backed by Postgres.
 *
 * Events live in a single `events` table; bucketing is pushed down to SQL via
 * `to_timestamp` + `date_trunc` so we never pull raw rows back for counts. The
 * `properties`/`geo`/`user_agent` columns are jsonb.
 */
export class PostgresEventStore implements EventStore {
  constructor(private readonly pool: Pool) {}

  /**
   * Build a store from the loaded config. Throws if the Postgres backend wasn't
   * configured — server.ts only calls this when STORAGE_BACKEND=postgres.
   */
  static fromConfig(): PostgresEventStore {
    const config = loadConfig();
    if (!config.postgresUrl) {
      throw new StorageError("PostgresEventStore requires config.postgresUrl");
    }
    const pool = new Pool({
      connectionString: config.postgresUrl,
      max: 10,
      idleTimeoutMillis: 30_000,
      application_name: "analytics-api",
    });
    return new PostgresEventStore(pool);
  }

  async insert(event: Event): Promise<void> {
    await this.insertBatch([event]);
  }

  /**
   * Multi-row INSERT in a single statement. We build a flat parameter list and
   * a `($1,$2,...),($n...)` VALUES clause so the whole batch is one round trip.
   */
  async insertBatch(events: Event[]): Promise<void> {
    if (events.length === 0) return;
    const cols = 10;
    const values: unknown[] = [];
    const tuples: string[] = [];

    events.forEach((e, i) => {
      const base = i * cols;
      tuples.push(
        `($${base + 1},$${base + 2},$${base + 3},to_timestamp($${base + 4}/1000.0),` +
          `$${base + 5},$${base + 6},$${base + 7},$${base + 8},$${base + 9},$${base + 10})`,
      );
      values.push(
        e.id,
        e.type,
        e.userId,
        e.serverTimestamp,
        e.clientTimestamp,
        JSON.stringify(e.properties),
        e.ip,
        e.geo ? JSON.stringify(e.geo) : null,
        e.userAgent ? JSON.stringify(e.userAgent) : null,
        e.apiKeyId,
      );
    });

    const sql =
      `INSERT INTO events ` +
      `(id, type, user_id, server_ts, client_ts, properties, ip, geo, user_agent, api_key_id) ` +
      `VALUES ${tuples.join(",")} ON CONFLICT (id) DO NOTHING`;

    try {
      await this.pool.query(sql, values);
    } catch (err) {
      throw new StorageError("failed to insert events", err);
    }
  }

  async queryRange(range: TimeRange, type?: EventType): Promise<Event[]> {
    const params: unknown[] = [msToTs(range.from), msToTs(range.to)];
    let sql =
      `SELECT id, type, user_id, ` +
      `extract(epoch from server_ts)*1000 AS server_ms, ` +
      `extract(epoch from client_ts)*1000 AS client_ms, ` +
      `properties, ip, geo, user_agent, api_key_id ` +
      `FROM events WHERE server_ts >= $1 AND server_ts < $2`;
    if (type) {
      params.push(type);
      sql += ` AND type = $3`;
    }
    sql += ` ORDER BY server_ts ASC`;

    try {
      const result = await this.pool.query(sql, params);
      return result.rows.map(rowToEvent);
    } catch (err) {
      throw new StorageError("queryRange failed", err);
    }
  }

  async countByType(query: CountQuery): Promise<TimeBucket[]> {
    const { range, type, granularity } = query;
    const params: unknown[] = [msToTs(range.from), msToTs(range.to)];
    const typeClause = type ? ` AND type = $3` : "";
    if (type) params.push(type);

    if (!granularity) {
      const sql =
        `SELECT count(*)::int AS n FROM events ` +
        `WHERE server_ts >= $1 AND server_ts < $2${typeClause}`;
      const { rows } = await this.pool.query(sql, params).catch(rethrow("count"));
      return [{ bucketStart: range.from, count: rows[0]?.n ?? 0 }];
    }

    const trunc = granularity === "hour" ? "hour" : "day";
    const sql =
      `SELECT date_trunc('${trunc}', server_ts) AS bucket, count(*)::int AS n ` +
      `FROM events WHERE server_ts >= $1 AND server_ts < $2${typeClause} ` +
      `GROUP BY bucket ORDER BY bucket`;
    const { rows } = await this.pool.query(sql, params).catch(rethrow("count"));

    const counts = new Map<number, number>();
    for (const r of rows) {
      counts.set(alignBucket(new Date(r.bucket).getTime(), granularity), r.n);
    }
    return buildBucketSeries(range, granularity, counts);
  }

  async distinctUsers(query: DistinctUsersQuery): Promise<number> {
    const params: unknown[] = [msToTs(query.range.from), msToTs(query.range.to)];
    const typeClause = query.type ? ` AND type = $3` : "";
    if (query.type) params.push(query.type);
    const sql =
      `SELECT count(DISTINCT user_id)::int AS n FROM events ` +
      `WHERE server_ts >= $1 AND server_ts < $2${typeClause}`;
    const { rows } = await this.pool
      .query(sql, params)
      .catch(rethrow("distinctUsers"));
    return rows[0]?.n ?? 0;
  }

  async close(): Promise<void> {
    await this.pool.end();
  }

  /** Run a callback inside a transaction; used by maintenance scripts. */
  async withTransaction<T>(fn: (client: PoolClient) => Promise<T>): Promise<T> {
    const client = await this.pool.connect();
    try {
      await client.query("BEGIN");
      const result = await fn(client);
      await client.query("COMMIT");
      return result;
    } catch (err) {
      await client.query("ROLLBACK");
      throw new StorageError("transaction rolled back", err);
    } finally {
      client.release();
    }
  }
}

function msToTs(ms: number): string {
  return new Date(ms).toISOString();
}

function alignBucket(ms: number, granularity: "hour" | "day"): number {
  const step = granularityMs(granularity);
  return ms - (ms % step);
}

function rethrow(op: string) {
  return (err: unknown): never => {
    throw new StorageError(`${op} failed`, err);
  };
}

interface EventRow {
  id: string;
  type: EventType;
  user_id: string;
  server_ms: string | number;
  client_ms: string | number | null;
  properties: Record<string, unknown> | null;
  ip: string | null;
  geo: Event["geo"];
  user_agent: Event["userAgent"];
  api_key_id: string;
}

function rowToEvent(row: EventRow): Event {
  return {
    id: row.id,
    type: row.type,
    userId: row.user_id,
    serverTimestamp: Number(row.server_ms),
    clientTimestamp: row.client_ms === null ? null : Number(row.client_ms),
    properties: row.properties ?? {},
    ip: row.ip,
    geo: row.geo,
    userAgent: row.user_agent,
    apiKeyId: row.api_key_id,
  };
}

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
 * ClickHouse-backed EventStore for high-volume deployments. Talks to ClickHouse
 * over its HTTP interface and leans on columnar aggregation (`toStartOfHour`,
 * `uniqExact`) for the metric queries. Inserts use JSONEachRow for batching.
 *
 * Selected via STORAGE_BACKEND=clickhouse. Postgres remains the default.
 */
export class ClickHouseEventStore implements EventStore {
  constructor(
    private readonly endpoint: string,
    private readonly database: string,
  ) {}

  static fromConfig(): ClickHouseEventStore {
    const config = loadConfig();
    if (!config.clickhouseUrl) {
      throw new StorageError(
        "ClickHouseEventStore requires config.clickhouseUrl",
      );
    }
    return new ClickHouseEventStore(
      config.clickhouseUrl,
      config.clickhouseDatabase,
    );
  }

  async insert(event: Event): Promise<void> {
    await this.insertBatch([event]);
  }

  async insertBatch(events: Event[]): Promise<void> {
    if (events.length === 0) return;
    // JSONEachRow: one JSON object per line, no enclosing array.
    const body = events.map((e) => JSON.stringify(toRow(e))).join("\n");
    await this.exec(
      `INSERT INTO ${this.database}.events FORMAT JSONEachRow`,
      body,
    );
  }

  async queryRange(range: TimeRange, type?: EventType): Promise<Event[]> {
    const where = this.rangeWhere(range, type);
    const sql =
      `SELECT id, type, user_id, ` +
      `toUnixTimestamp64Milli(server_ts) AS server_ms, ` +
      `toUnixTimestamp64Milli(client_ts) AS client_ms, ` +
      `properties, ip, geo, user_agent, api_key_id ` +
      `FROM ${this.database}.events WHERE ${where} ` +
      `ORDER BY server_ts ASC FORMAT JSON`;
    const json = await this.query<RowJson>(sql);
    return json.data.map(rowToEvent);
  }

  async countByType(query: CountQuery): Promise<TimeBucket[]> {
    const { range, granularity } = query;
    const where = this.rangeWhere(range, query.type);

    if (!granularity) {
      const sql = `SELECT count() AS n FROM ${this.database}.events WHERE ${where} FORMAT JSON`;
      const json = await this.query<{ n: string }>(sql);
      return [{ bucketStart: range.from, count: Number(json.data[0]?.n ?? 0) }];
    }

    const fn = granularity === "hour" ? "toStartOfHour" : "toStartOfDay";
    const sql =
      `SELECT toUnixTimestamp64Milli(toDateTime64(${fn}(server_ts), 3)) AS bucket, ` +
      `count() AS n FROM ${this.database}.events WHERE ${where} ` +
      `GROUP BY bucket ORDER BY bucket FORMAT JSON`;
    const json = await this.query<{ bucket: string; n: string }>(sql);

    const counts = new Map<number, number>();
    for (const r of json.data) {
      counts.set(alignBucket(Number(r.bucket), granularity), Number(r.n));
    }
    return buildBucketSeries(range, granularity, counts);
  }

  async distinctUsers(query: DistinctUsersQuery): Promise<number> {
    const where = this.rangeWhere(query.range, query.type);
    const sql = `SELECT uniqExact(user_id) AS n FROM ${this.database}.events WHERE ${where} FORMAT JSON`;
    const json = await this.query<{ n: string }>(sql);
    return Number(json.data[0]?.n ?? 0);
  }

  async close(): Promise<void> {
    // Stateless HTTP client; nothing pooled to tear down.
  }

  private rangeWhere(range: TimeRange, type?: EventType): string {
    const clauses = [
      `server_ts >= fromUnixTimestamp64Milli(${range.from})`,
      `server_ts < fromUnixTimestamp64Milli(${range.to})`,
    ];
    if (type) clauses.push(`type = ${quote(type)}`);
    return clauses.join(" AND ");
  }

  private async query<T>(sql: string): Promise<{ data: T[] }> {
    const text = await this.exec(sql);
    try {
      return JSON.parse(text) as { data: T[] };
    } catch (err) {
      throw new StorageError("could not parse ClickHouse response", err);
    }
  }

  private async exec(sql: string, body?: string): Promise<string> {
    const url = `${this.endpoint}/?query=${encodeURIComponent(sql)}`;
    let res: Response;
    try {
      res = await fetch(url, {
        method: "POST",
        body: body ?? null,
        headers: { "Content-Type": "text/plain" },
      });
    } catch (err) {
      throw new StorageError("ClickHouse request failed", err);
    }
    const text = await res.text();
    if (!res.ok) {
      throw new StorageError(`ClickHouse ${res.status}: ${text.slice(0, 500)}`);
    }
    return text;
  }
}

function quote(s: string): string {
  return `'${s.replace(/'/g, "\\'")}'`;
}

function alignBucket(ms: number, granularity: "hour" | "day"): number {
  const step = granularityMs(granularity);
  return ms - (ms % step);
}

function toRow(e: Event): Record<string, unknown> {
  return {
    id: e.id,
    type: e.type,
    user_id: e.userId,
    server_ts: e.serverTimestamp,
    client_ts: e.clientTimestamp ?? 0,
    properties: JSON.stringify(e.properties),
    ip: e.ip ?? "",
    geo: e.geo ? JSON.stringify(e.geo) : "",
    user_agent: e.userAgent ? JSON.stringify(e.userAgent) : "",
    api_key_id: e.apiKeyId,
  };
}

interface RowJson {
  data: Array<{
    id: string;
    type: EventType;
    user_id: string;
    server_ms: string | number;
    client_ms: string | number;
    properties: string;
    ip: string;
    geo: string;
    user_agent: string;
    api_key_id: string;
  }>;
}

function rowToEvent(
  row: RowJson["data"][number],
): Event {
  return {
    id: row.id,
    type: row.type,
    userId: row.user_id,
    serverTimestamp: Number(row.server_ms),
    clientTimestamp: row.client_ms ? Number(row.client_ms) : null,
    properties: row.properties ? JSON.parse(row.properties) : {},
    ip: row.ip || null,
    geo: row.geo ? JSON.parse(row.geo) : null,
    userAgent: row.user_agent ? JSON.parse(row.user_agent) : null,
    apiKeyId: row.api_key_id,
  };
}

import type { BucketGranularity, TimeRange, TimeBucket } from "../store/store";

export const HOUR_MS = 60 * 60 * 1000;
export const DAY_MS = 24 * HOUR_MS;

export function granularityMs(granularity: BucketGranularity): number {
  return granularity === "hour" ? HOUR_MS : DAY_MS;
}

/**
 * Floor an epoch-millis timestamp down to the start of its UTC hour.
 * We deliberately work in UTC everywhere so buckets are comparable across
 * regions; callers that need local time should shift on the way out.
 */
export function floorToHour(ts: number): number {
  return ts - (ts % HOUR_MS);
}

/** Floor to the start of the UTC day. */
export function floorToDay(ts: number): number {
  return ts - (ts % DAY_MS);
}

export function floorTo(ts: number, granularity: BucketGranularity): number {
  return granularity === "hour" ? floorToHour(ts) : floorToDay(ts);
}

/**
 * Error raised when a caller-supplied range can't be parsed or is nonsensical
 * (from after to, absurd width, etc.). Routes translate this to a 400.
 */
export class RangeError_ extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RangeError";
  }
}

/** Hard cap so a single query can't ask for an unbounded scan. */
export const MAX_RANGE_MS = 92 * DAY_MS;

/**
 * Parse a `from`/`to` query pair into a validated TimeRange.
 *
 * Accepts either epoch-millis integers or ISO-8601 strings. Defaults: `to`
 * defaults to now, `from` defaults to 24h before `to`. Throws RangeError_ on
 * anything inverted, non-finite, or wider than MAX_RANGE_MS.
 */
export function parseRange(
  rawFrom: string | undefined,
  rawTo: string | undefined,
  now: number = Date.now(),
): TimeRange {
  const to = rawTo === undefined ? now : parseInstant(rawTo, "to");
  const from =
    rawFrom === undefined ? to - DAY_MS : parseInstant(rawFrom, "from");

  if (!Number.isFinite(from) || !Number.isFinite(to)) {
    throw new RangeError_("range bounds must be finite");
  }
  if (from >= to) {
    throw new RangeError_("`from` must be strictly before `to`");
  }
  if (to - from > MAX_RANGE_MS) {
    throw new RangeError_(
      `range too wide: max ${MAX_RANGE_MS}ms, got ${to - from}ms`,
    );
  }
  return { from, to };
}

function parseInstant(raw: string, field: string): number {
  const asNumber = Number(raw);
  if (Number.isFinite(asNumber) && /^\d+$/.test(raw.trim())) {
    return asNumber;
  }
  const parsed = Date.parse(raw);
  if (Number.isNaN(parsed)) {
    throw new RangeError_(`could not parse \`${field}\`: ${raw}`);
  }
  return parsed;
}

/**
 * Build a dense, zero-filled bucket series across the range. Backends that only
 * return non-empty buckets feed their rows in via `counts`; gaps become zeros so
 * the client always gets a regular grid.
 */
export function buildBucketSeries(
  range: TimeRange,
  granularity: BucketGranularity,
  counts: Map<number, number>,
): TimeBucket[] {
  const step = granularityMs(granularity);
  const start = floorTo(range.from, granularity);
  const buckets: TimeBucket[] = [];
  for (let t = start; t < range.to; t += step) {
    buckets.push({ bucketStart: t, count: counts.get(t) ?? 0 });
  }
  return buckets;
}

export function isWithin(ts: number, range: TimeRange): boolean {
  return ts >= range.from && ts < range.to;
}

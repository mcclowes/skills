import { Router, type Request, type Response } from "express";
import { EVENT_TYPES, type BucketGranularity, type EventType } from "../store/store";
import { parseRange, RangeError_ } from "../lib/time";
import type { AggregationService } from "../services/aggregation";

/**
 * Read-side query routes. Each handler parses + validates query params, calls
 * the AggregationService, and serialises the MetricResult. Bad params produce a
 * 400; everything else is delegated.
 *
 *   GET /v1/metrics/count          total / bucketed counts
 *   GET /v1/metrics/unique-users   distinct users
 *   GET /v1/metrics/top-types      event-type leaderboard
 */
export function queryRouter(aggregation: AggregationService): Router {
  const router = Router();

  router.get("/v1/metrics/count", async (req: Request, res: Response) => {
    let range;
    let type: EventType | undefined;
    let granularity: BucketGranularity | undefined;
    try {
      range = parseRange(strParam(req, "from"), strParam(req, "to"));
      type = parseType(strParam(req, "type"));
      granularity = parseGranularity(strParam(req, "granularity"));
    } catch (err) {
      return sendParamError(err, res);
    }

    const result = await aggregation.count({ range, type, granularity });
    res.json(result);
  });

  router.get(
    "/v1/metrics/unique-users",
    async (req: Request, res: Response) => {
      let range;
      let type: EventType | undefined;
      try {
        range = parseRange(strParam(req, "from"), strParam(req, "to"));
        type = parseType(strParam(req, "type"));
      } catch (err) {
        return sendParamError(err, res);
      }

      const result = await aggregation.uniqueUsers({ range, type });
      res.json(result);
    },
  );

  router.get("/v1/metrics/top-types", async (req: Request, res: Response) => {
    let range;
    let limit: number | undefined;
    try {
      range = parseRange(strParam(req, "from"), strParam(req, "to"));
      limit = parseLimit(strParam(req, "limit"));
    } catch (err) {
      return sendParamError(err, res);
    }

    const results = await aggregation.topEventTypes({ range, limit });
    res.json({ range, results });
  });

  return router;
}

/** Express query values can be string | string[] | undefined; flatten safely. */
function strParam(req: Request, name: string): string | undefined {
  const v = req.query[name];
  if (Array.isArray(v)) return typeof v[0] === "string" ? v[0] : undefined;
  return typeof v === "string" ? v : undefined;
}

function parseType(raw: string | undefined): EventType | undefined {
  if (raw === undefined) return undefined;
  if (!EVENT_TYPES.includes(raw as EventType)) {
    throw new RangeError_(`unknown event type "${raw}"`);
  }
  return raw as EventType;
}

function parseGranularity(
  raw: string | undefined,
): BucketGranularity | undefined {
  if (raw === undefined) return undefined;
  if (raw !== "hour" && raw !== "day") {
    throw new RangeError_(`granularity must be "hour" or "day", got "${raw}"`);
  }
  return raw;
}

function parseLimit(raw: string | undefined): number | undefined {
  if (raw === undefined) return undefined;
  const n = Number.parseInt(raw, 10);
  if (Number.isNaN(n) || n < 1 || n > 100) {
    throw new RangeError_("limit must be an integer in [1, 100]");
  }
  return n;
}

function sendParamError(err: unknown, res: Response): void {
  if (err instanceof RangeError_) {
    res.status(400).json({
      error: { code: "bad_request", message: err.message },
    });
    return;
  }
  res.status(500).json({
    error: { code: "internal", message: "failed to run query" },
  });
}

/**
 * ---
 * purpose: HTTP write endpoints (POST /v1/events, /v1/events/batch) — thin handlers that build RequestMeta from the connection/headers (X-Forwarded-For for IP), delegate to IngestionService, and map errors to status codes (400/207/413/500).
 * related:
 *   - ../services/ingestion.ts - does all validation/enrichment/persistence; handlers just call ingest/ingestBatch
 *   - ../services/enrichment.ts - defines the RequestMeta shape these handlers populate
 *   - ../lib/validate.ts - source of the ValidationError mapped to a structured 400 here
 *   - ../middleware/auth.ts - guarantees req.auth is set, so requestMeta can read apiKeyId
 * ---
 */
import { Router, type Request, type Response } from "express";
import { ValidationError } from "../lib/validate";
import type { IngestionService } from "../services/ingestion";
import type { RequestMeta } from "../services/enrichment";

/**
 * Ingest routes. The handlers are thin: build the RequestMeta from the
 * connection/headers, delegate to IngestionService, and translate domain errors
 * into HTTP. All validation/enrichment/persistence lives in the service.
 *
 *   POST /v1/events        single event
 *   POST /v1/events/batch  array of events (partial success)
 */
export function ingestRouter(ingestion: IngestionService): Router {
  const router = Router();

  router.post("/v1/events", async (req: Request, res: Response) => {
    const meta = requestMeta(req);
    try {
      const result = await ingestion.ingest(req.body, meta);
      res.status(202).json({
        eventId: result.eventId,
        serverTimestamp: result.serverTimestamp,
      });
    } catch (err) {
      handleIngestError(err, res);
    }
  });

  router.post("/v1/events/batch", async (req: Request, res: Response) => {
    if (!Array.isArray(req.body)) {
      res.status(400).json({
        error: {
          code: "malformed",
          message: "batch endpoint expects a JSON array of events",
        },
      });
      return;
    }
    if (req.body.length > MAX_BATCH) {
      res.status(413).json({
        error: {
          code: "batch_too_large",
          message: `batch exceeds ${MAX_BATCH} events`,
        },
      });
      return;
    }

    const meta = requestMeta(req);
    try {
      const result = await ingestion.ingestBatch(req.body, meta);
      // 207 when some items failed, 202 when everything was accepted.
      const status = result.rejected > 0 ? 207 : 202;
      res.status(status).json(result);
    } catch (err) {
      handleIngestError(err, res);
    }
  });

  return router;
}

const MAX_BATCH = 1000;

/**
 * Derive request metadata from the connection. The source IP prefers the first
 * hop in X-Forwarded-For (we sit behind a proxy) and falls back to the socket.
 * `req.auth` is guaranteed set because apiKeyAuth runs before these routes.
 */
function requestMeta(req: Request): RequestMeta {
  const forwarded = req.header("x-forwarded-for");
  const ip = forwarded
    ? forwarded.split(",")[0]!.trim()
    : (req.socket.remoteAddress ?? null);

  return {
    ip,
    userAgent: req.header("user-agent") ?? null,
    apiKeyId: req.auth!.apiKeyId,
  };
}

function handleIngestError(err: unknown, res: Response): void {
  if (err instanceof ValidationError) {
    res.status(400).json({
      error: {
        code: err.code,
        field: err.field,
        message: err.message,
      },
    });
    return;
  }
  res.status(500).json({
    error: { code: "internal", message: "failed to ingest event" },
  });
}

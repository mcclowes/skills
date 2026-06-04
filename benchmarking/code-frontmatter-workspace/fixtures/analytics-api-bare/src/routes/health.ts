import { Router, type Request, type Response } from "express";
import type { EventStore } from "../store/store";

/**
 * Liveness and readiness endpoints.
 *
 *   GET /healthz   liveness — process is up; never touches storage.
 *   GET /readyz    readiness — runs a trivial store query to prove the backend
 *                  is reachable; returns 503 if it isn't, so load balancers can
 *                  drain an instance that lost its database.
 *
 * Neither route requires auth; they're mounted before the auth middleware.
 */
export function healthRouter(store: EventStore): Router {
  const router = Router();
  const startedAt = Date.now();

  router.get("/healthz", (_req: Request, res: Response) => {
    res.json({
      status: "ok",
      uptimeMs: Date.now() - startedAt,
    });
  });

  router.get("/readyz", async (_req: Request, res: Response) => {
    try {
      // Cheapest possible probe: count over a zero-width-ish recent window.
      const now = Date.now();
      await store.countByType({ range: { from: now - 1000, to: now } });
      res.json({ status: "ready" });
    } catch {
      res.status(503).json({
        status: "unavailable",
        reason: "storage backend unreachable",
      });
    }
  });

  return router;
}

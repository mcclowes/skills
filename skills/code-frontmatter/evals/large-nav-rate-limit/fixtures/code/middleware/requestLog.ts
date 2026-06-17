/**
 * ---
 * purpose: Structured JSON-per-line request logger — assigns/echoes a requestId (honouring inbound X-Request-Id) and emits one line on response finish with method, path, status, duration, and api key id, filtered by config.logLevel.
 * related:
 *   - ../config.ts - reads config.logLevel to set the suppression threshold
 *   - ../server.ts - mounted first so every request (even health checks) is logged
 *   - ./auth.ts - reads the req.auth.apiKeyId that auth attaches, when present
 * ---
 */
import { randomUUID } from "node:crypto";
import type { NextFunction, Request, Response } from "express";
import type { Config } from "../config";

declare module "express-serve-static-core" {
  interface Request {
    requestId?: string;
  }
}

const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 } as const;
type Level = keyof typeof LEVELS;

interface LogLine {
  level: Level;
  msg: string;
  requestId: string;
  method: string;
  path: string;
  status?: number;
  durationMs?: number;
  apiKeyId?: string;
  [extra: string]: unknown;
}

/**
 * Structured (JSON-per-line) request logger.
 *
 * Assigns a `requestId` (honouring an inbound `X-Request-Id` if present),
 * echoes it back on the response header, and emits one line when the response
 * finishes with method, path, status, duration and the authenticated key id.
 * Lines below the configured `logLevel` are suppressed.
 */
export function requestLogger(config: Config, sink: LogSink = consoleSink) {
  const threshold = LEVELS[config.logLevel];

  return (req: Request, res: Response, next: NextFunction): void => {
    const requestId = req.header("x-request-id") ?? randomUUID();
    req.requestId = requestId;
    res.setHeader("X-Request-Id", requestId);

    const startedAt = process.hrtime.bigint();

    res.on("finish", () => {
      const durationMs =
        Number(process.hrtime.bigint() - startedAt) / 1_000_000;
      const level: Level = res.statusCode >= 500 ? "error" : "info";
      if (LEVELS[level] < threshold) return;

      sink({
        level,
        msg: "request",
        requestId,
        method: req.method,
        path: req.path,
        status: res.statusCode,
        durationMs: Math.round(durationMs * 100) / 100,
        apiKeyId: req.auth?.apiKeyId,
      });
    });

    next();
  };
}

export type LogSink = (line: LogLine) => void;

const consoleSink: LogSink = (line) => {
  const stream = line.level === "error" ? process.stderr : process.stdout;
  stream.write(JSON.stringify({ ts: new Date().toISOString(), ...line }) + "\n");
};

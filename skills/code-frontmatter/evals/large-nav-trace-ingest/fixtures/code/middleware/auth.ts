/**
 * ---
 * purpose: API-key auth middleware — accepts a key from X-API-Key or Authorization: Bearer, returns 401 (missing) vs 403 (unknown), and on success sets req.auth.apiKeyId for the rate limiter and logger.
 * related:
 *   - ../config.ts - looks up the presented key in config.apiKeys (key -> keyId map)
 *   - ../server.ts - mounts this as the auth wall, after healthRouter and before rateLimit/routes
 *   - ./rateLimit.ts - consumes the req.auth.apiKeyId set here as the bucket key
 *   - ./requestLog.ts - reads req.auth.apiKeyId to attribute log lines
 * ---
 *
 * Fields the auth middleware attaches to the request once a key is accepted.
 * Downstream middleware/handlers read `req.auth` rather than re-parsing headers.
 */
export interface AuthContext {
  /** Stable id for the key (see config API_KEYS parsing); buckets rate limits. */
  apiKeyId: string;
}

declare module "express-serve-static-core" {
  interface Request {
    auth?: AuthContext;
  }
}

const BEARER_PREFIX = /^Bearer\s+/i;

/**
 * API-key authentication.
 *
 * Accepts the key from either the `X-API-Key` header or an
 * `Authorization: Bearer <key>` header. Missing keys get 401; present-but-unknown
 * keys get 403 so clients can distinguish "you sent nothing" from "your key is
 * wrong". On success, `req.auth.apiKeyId` is set for rate limiting and logging.
 */
export function apiKeyAuth(config: Config) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const presented = extractKey(req);

    if (!presented) {
      res.status(401).json({
        error: { code: "missing_api_key", message: "API key required" },
      });
      return;
    }

    const apiKeyId = config.apiKeys.get(presented);
    if (!apiKeyId) {
      res.status(403).json({
        error: { code: "invalid_api_key", message: "API key not recognised" },
      });
      return;
    }

    req.auth = { apiKeyId };
    next();
  };
}

function extractKey(req: Request): string | null {
  const headerKey = req.header("x-api-key");
  if (headerKey && headerKey.trim() !== "") {
    return headerKey.trim();
  }
  const authz = req.header("authorization");
  if (authz && BEARER_PREFIX.test(authz)) {
    return authz.replace(BEARER_PREFIX, "").trim();
  }
  return null;
}

/**
 * ---
 * purpose: Validates/normalises a target URL - http(s) only, with a basic private/loopback SSRF guard.
 * related:
 *   - ./shortener.ts - calls validateTarget before storing
 * ---
 */
const ALLOWED_PROTOCOLS = new Set(["http:", "https:"]);

export interface ValidationResult {
  ok: boolean;
  normalised?: string;
  reason?: string;
}

/**
 * A target is valid if it parses as an absolute http(s) URL and is not a
 * loopback/private address (basic SSRF guard for the fixture).
 */
export function validateTarget(raw: string): ValidationResult {
  let url: URL;
  try {
    url = new URL(raw);
  } catch {
    return { ok: false, reason: "not a valid absolute URL" };
  }
  if (!ALLOWED_PROTOCOLS.has(url.protocol)) {
    return { ok: false, reason: `protocol ${url.protocol} not allowed` };
  }
  if (isPrivateHost(url.hostname)) {
    return { ok: false, reason: "refusing to shorten a private/loopback host" };
  }
  url.hash = "";
  return { ok: true, normalised: url.toString() };
}

function isPrivateHost(host: string): boolean {
  return (
    host === "localhost" ||
    host === "127.0.0.1" ||
    host.startsWith("10.") ||
    host.startsWith("192.168.") ||
    host.endsWith(".local")
  );
}

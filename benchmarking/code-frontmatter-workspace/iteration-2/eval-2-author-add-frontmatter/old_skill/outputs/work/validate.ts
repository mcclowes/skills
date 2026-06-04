/**
 * ---
 * purpose: Validate/normalise a shorten target - http(s) only, basic SSRF guard against private/loopback hosts
 * exports:
 *   - validateTarget - returns { ok, normalised?, reason? }
 *   - ValidationResult - result shape
 * related:
 *   - ./shortener.ts - calls this before storing a link
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

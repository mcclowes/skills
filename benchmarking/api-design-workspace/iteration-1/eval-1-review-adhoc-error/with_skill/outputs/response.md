# Review: API error response for failed auth

## Your current response

```json
{ "error": "Unauthorized", "code": 401, "msg": "token bad" }
```

This works, but it has a few problems that will bite you as soon as you have more than one endpoint and more than one consumer.

## Critique

1. **Numeric `code` adds nothing.** `401` is already in the HTTP status line. Repeating it in the body just gives clients two places to read the same thing — and a numeric code like this tempts people toward an opaque `4012`-style lookup-table system later. A descriptive string code tells a developer what happened without a reference table.

2. **`"token bad"` is doing three jobs badly.** It's the machine-readable reason, the developer-facing explanation, and (implicitly) the thing you'd show a user — all in one ambiguous string. A client can't branch on it reliably (is it `token bad`, `bad token`, `token_expired`?), and it's not something you'd ever put in front of an end user.

3. **No traceability.** There's no correlation/request ID. When an integrator emails you "auth is failing," you have nothing to grep your logs for. This is the single most valuable field to add and it's missing.

4. **No path to resolution.** Nothing tells the developer *why* the token is bad (expired? malformed? revoked?) or what to do next (re-auth endpoint, docs link, support portal). "token bad" forces guesswork.

5. **Inconsistent keys across endpoints.** `error` / `code` / `msg` is an ad-hoc trio. The moment another endpoint returns `errors: [...]` or `detail: "..."`, every consumer has to special-case each endpoint. You need *one* shape everywhere.

6. **No room for multiple problems or for warnings.** A single flat object can only express one error. Validation endpoints routinely have several issues at once, and you'll eventually want to surface non-blocking warnings on otherwise-successful responses. A flat object can't grow into that without a breaking change.

## Recommended shape

Adopt a single `issues` array used by **every** non-success response (and optionally for warnings on 2xx responses). Every issue shares one shape, so a client writes one handler for the whole API.

For your specific failed-auth case (expired token):

```json
{
  "issues": [
    {
      "type": "unauthorized",
      "issue": "unauthorized.token_expired",
      "severity": "error",
      "correlationId": "4b3a2c1d-0000-0000-0000-abcdef123456",
      "dateTime": "2026-06-03T12:34:56Z",
      "active": false,
      "message": {
        "title": "Session expired",
        "detail": "Your access token has expired. Request a new token and retry."
      },
      "links": {
        "documentation": "https://docs.example.com/errors/unauthorized",
        "portal": "https://support.example.com",
        "api": "https://api.example.com/auth/token"
      }
    }
  ]
}
```

### What each field buys you (mapped to your old fields)

| Old | New | Why |
|---|---|---|
| `error: "Unauthorized"` | `type: "unauthorized"` | Stable, small, enumerated top-level category. Keep this set short (`unauthorized`, `validation`, `conflict`, `rate_limit`, `internal`). |
| `code: 401` | (drop) | Already in the HTTP status line; don't duplicate. The actionable code is now `issue`. |
| `msg: "token bad"` | `issue: "unauthorized.token_expired"` | Descriptive, namespaced `{type}.{detail}` machine code. A developer can branch on it without a lookup table, and `unauthorized.token_expired` vs `unauthorized.token_malformed` read as obviously related. |
| — | `severity: "error"` | Distinguishes blocking errors from advisory `warning` / `info`, so warnings can ride along on the same array. |
| — | `correlationId` | The single most useful addition: one ID to find this exact request in your logs. Generate one per request; if the client sends `X-Correlation-ID`, echo it back. |
| — | `dateTime` | ISO 8601 UTC; when it happened. |
| — | `active` | Resolution state. For an expired token the issue clears on re-auth, so `false`. **Omit this field entirely if you can't track resolution reliably** — a stale `active: true` is worse than nothing. |
| — | `message` | Human-readable `{ title, detail }`, English-only, safe to show end users. A convenience — integrators may override the copy and own localisation. |
| — | `links` | `documentation` / `portal` / `api` to help the developer act. Here `api` points at your token endpoint so they know exactly where to re-auth. |

There's also an optional `thirdParty: { provider, code, message }` for issues that originate upstream (e.g. an identity provider) — pass it through verbatim, never branch your logic on it, and don't assume it's fit for end users. Not needed for this auth case.

## Design rules to apply across all endpoints

- **One `issues` array, everywhere.** Same shape in responses, webhooks, and callbacks. This is the consistency win you're asking for.
- **String codes, not numbers.** `validation.missing_field`, not `4012`.
- **Namespace as `{type}.{detail}`.** Hierarchy without exploding the `type` enum.
- **Keep `issue` a plain string, not a strict enum — at least early on.** The taxonomy will grow; a strict enum makes every new code a breaking change. Tell consumers to handle unknown values gracefully (fall back to `type`).
- **Always generate `correlationId`; echo `X-Correlation-ID` when supplied.**
- **Omit `active` rather than lie about it.**
- **`message` is for humans, `issue` is for code.** Never make clients parse `message` to decide behaviour.

## A few examples to standardise on

Validation failure with multiple problems (note: several issues, one array):

```json
{
  "issues": [
    {
      "type": "validation",
      "issue": "validation.missing_field",
      "severity": "error",
      "correlationId": "9f1e...",
      "dateTime": "2026-06-03T12:35:01Z",
      "message": { "title": "Email required", "detail": "The 'email' field is required." }
    },
    {
      "type": "validation",
      "issue": "validation.invalid_format",
      "severity": "error",
      "correlationId": "9f1e...",
      "dateTime": "2026-06-03T12:35:01Z",
      "message": { "title": "Invalid amount", "detail": "'amount' must be a positive integer." }
    }
  ]
}
```

Rate limit, with a `warning` that you can act on:

```json
{
  "issues": [
    {
      "type": "rate_limit",
      "issue": "rate_limit.exceeded",
      "severity": "error",
      "correlationId": "aa00...",
      "dateTime": "2026-06-03T12:36:10Z",
      "message": { "title": "Too many requests", "detail": "Retry after 30 seconds." },
      "links": { "documentation": "https://docs.example.com/errors/rate-limit" }
    }
  ]
}
```

## Consuming it (TypeScript)

So clients can branch cleanly and never parse `message`:

```ts
type Severity = "error" | "warning" | "info";

interface Issue {
  type: string;          // category — handle unknown values gracefully
  issue: string;         // {type}.{detail}, e.g. "unauthorized.token_expired"
  severity: Severity;
  correlationId: string;
  dateTime: string;      // ISO 8601 UTC
  active?: boolean;
  message?: { title: string; detail: string };
  thirdParty?: { provider: string; code?: string; message?: string };
  links?: { documentation?: string; portal?: string; api?: string };
}

interface ErrorResponse {
  issues: Issue[];
}

// Example handler: re-auth on expired token, otherwise surface the message.
function handle(res: ErrorResponse) {
  const fatal = res.issues.filter((i) => i.severity === "error");
  if (fatal.some((i) => i.issue === "unauthorized.token_expired")) {
    return refreshTokenAndRetry();
  }
  // Fall back to type, then to the human message, so unknown codes still work.
  showToast(fatal[0]?.message?.title ?? fatal[0]?.type ?? "Request failed");
}
```

## Migration note

This is additive and low-risk: ship the `issues` array alongside the old `error`/`code`/`msg` fields for a deprecation window, tell integrators to switch, then remove the legacy keys in a future version. Document `issue` codes as a growing, non-exhaustive list so adding new ones never breaks a client that handles unknowns gracefully.

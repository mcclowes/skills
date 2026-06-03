# API error response review

## Your current response

```json
{ "error": "Unauthorized", "code": 401, "msg": "token bad" }
```

This works, but it has several problems that will bite you as the API grows and as more developers integrate against it.

## Critique

**1. `code: 401` duplicates the HTTP status and invites ambiguity.**
The HTTP status line already carries `401`. Repeating it in the body is redundant, and worse, a numeric `code` field reads ambiguously: is it the HTTP status, or an application-specific error number? Clients can't tell. If you ever want a stable, machine-readable error identifier (you do), a number forces you into an opaque lookup table that everyone has to maintain.

**2. There's no stable, machine-readable error identifier.**
`"error": "Unauthorized"` is the HTTP reason phrase, not an application error code. Clients shouldn't branch on it. They need a stable string token (e.g. `token_expired` vs `token_invalid` vs `token_missing`) that never changes once shipped, so they can write reliable conditional logic. "Unauthorized" lumps every auth failure together.

**3. Field names are inconsistent and abbreviated.**
`msg` instead of `message`, `error` carrying a human label, `code` carrying a number. Abbreviations like `msg` save nothing and create guessing games. Pick full, predictable names and use them on every endpoint.

**4. The message is for machines-formatted humans, but unhelpfully terse.**
`"token bad"` tells a developer almost nothing. Why is it bad? Expired? Malformed? Revoked? Wrong audience? A good message is human-readable and actionable, while the *code* stays machine-stable.

**5. No way to correlate with your logs.**
When a developer emails "I got a 401 at 2pm," you have nothing to grep for. A request/trace ID in every error response makes support dramatically faster.

**6. No path to richer errors.**
The flat shape can't express validation errors with multiple field-level problems. If you standardize now, a `details` array gives you room to grow without a second breaking redesign later.

**7. Consistency across endpoints isn't enforced by the shape.**
The biggest win of a standard envelope is that *every* endpoint returns the same structure, so clients write one error handler. The current ad-hoc shape doesn't signal a contract.

## Recommended structure

Use a single, consistent envelope with a top-level `error` object. Keep the HTTP status as the transport-level signal and put a **stable string `code`** in the body for machine branching.

### For the failed-auth example

```json
{
  "error": {
    "code": "token_invalid",
    "message": "The access token is invalid or has expired.",
    "status": 401,
    "request_id": "req_8f3a2c9b1d",
    "documentation_url": "https://docs.example.com/errors/token_invalid"
  }
}
```

### Field reference

| Field | Type | Required | Purpose |
|---|---|---|---|
| `error.code` | string | yes | Stable, snake_case, machine-readable token. Never changes once published. Clients branch on this. |
| `error.message` | string | yes | Human-readable, actionable explanation. Safe to change; not for branching. |
| `error.status` | number | yes | Mirrors the HTTP status, convenient for clients that only see the body (e.g. logged payloads). |
| `error.request_id` | string | yes | Correlates with your server logs for support and debugging. |
| `error.documentation_url` | string | optional | Deep link to docs for this error code. Optional but very developer-friendly. |
| `error.details` | array | optional | Field-level breakdown for validation and multi-error cases (see below). |

### Validation / multi-error example

The same envelope scales to richer errors via `details`:

```json
{
  "error": {
    "code": "validation_failed",
    "message": "One or more fields are invalid.",
    "status": 422,
    "request_id": "req_1a2b3c4d5e",
    "details": [
      { "field": "email", "code": "invalid_format", "message": "Must be a valid email address." },
      { "field": "age", "code": "out_of_range", "message": "Must be between 0 and 120." }
    ]
  }
}
```

## Guidelines to make this consistent across all endpoints

1. **One envelope, everywhere.** Every non-2xx response returns a top-level `error` object with this shape. No exceptions, including 500s.
2. **HTTP status is the source of truth for category** (4xx client, 5xx server). The `error.code` string gives the specific reason.
3. **`error.code` values are a published, append-only enum.** Document each one. Never rename or repurpose an existing code; that's a breaking change for clients.
4. **Use the right status codes.** For auth specifically: `401` for missing/invalid/expired credentials, `403` for authenticated-but-not-permitted. Don't return `403` with a `token_invalid` code.
5. **Always include `request_id`**, and log it server-side so support can trace it.
6. **Never leak internals.** No stack traces, SQL, or internal hostnames in `message`. For 5xx, use a generic message plus the `request_id`.
7. **Codify it once.** Implement a single error-serialization middleware/helper so individual handlers just throw a typed error and the shape is guaranteed.

## Summary of the change

| Before | After |
|---|---|
| `"error": "Unauthorized"` (HTTP phrase) | `"error.code": "token_invalid"` (stable machine token) |
| `"code": 401` (ambiguous number) | `"error.status": 401` (clearly the HTTP status) |
| `"msg": "token bad"` (terse, abbreviated) | `"error.message": "The access token is invalid or has expired."` |
| no correlation ID | `"error.request_id": "req_..."` |
| flat, can't grow | nestable `error.details` for validation |

The net effect: one predictable shape across every endpoint, a stable code clients can safely branch on, human messages you can freely improve, and a request ID that makes support tractable.

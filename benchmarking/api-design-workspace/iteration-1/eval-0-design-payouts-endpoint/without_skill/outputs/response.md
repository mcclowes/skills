# Error response design for `POST /api/v1/payouts`

## Design goals

A good error body should let three different consumers each do their job from a single response:

1. **Client code** — branch on a stable, machine-readable `code` (never on HTTP status alone, never on the human message).
2. **The end user** — see a safe, human-readable `message` that can be shown in the UI.
3. **An engineer debugging an incident** — correlate the failure via a `request_id` and inspect structured `details`.

Principles applied below:

- **Consistent envelope.** Every error, regardless of cause, has the same top-level shape. Clients write one parser, not three.
- **Stable string `code`s, not magic numbers.** Codes are part of your API contract; document them and never reuse/repurpose them.
- **HTTP status reflects the category; `code` reflects the specific reason.** Several distinct `code`s can share one status (e.g. two different `422`s).
- **Don't leak the vendor as your contract.** Sequra is an implementation detail. Surface a stable error of your own and tuck the raw provider data into `details.provider` for debugging, so that swapping providers later doesn't break clients.
- **Actionable `details`.** For limit errors, return the numbers the client needs to render a useful message without a second API call.
- **Always include a correlation id** so support/logs can be tied to a specific request.

## The envelope

```jsonc
{
  "error": {
    "code": "string",        // stable, machine-readable, SCREAMING_SNAKE_CASE
    "message": "string",     // human-readable, safe to show end users
    "details": { },          // optional, case-specific structured data
    "request_id": "string"   // correlation id, present on every response
  }
}
```

## Choosing the right HTTP status per case

| Case | HTTP status | `code` | Why |
|------|-------------|--------|-----|
| Bank token expired | `401 Unauthorized` | `BANK_TOKEN_EXPIRED` | The credential the action depends on is no longer valid; client must re-authenticate the bank connection. (Use `403`/`409` instead if you treat the API caller as authenticated and only the *linked account* is stale — see note below.) |
| Amount exceeds daily limit | `422 Unprocessable Entity` | `PAYOUT_LIMIT_EXCEEDED` | Request is well-formed and authorized, but violates a business rule. |
| Sequra rejects it | `502 Bad Gateway` | `PROVIDER_REJECTED` | An upstream dependency we called returned a failure. `502`/`503` signals "not necessarily your fault" and supports retry semantics. |

> Note on the token case: `401` is the conventional choice and pairs well with a `WWW-Authenticate`-style "re-link your bank" flow on the client. If your auth model is "the user is logged in; only their *bank link* expired," some teams prefer `409 Conflict` or `403 Forbidden` so a generic `401` interceptor doesn't bounce the user out of the app entirely. Pick one and be consistent across the API.

---

## Concrete responses

### 1. Bank token expired — `401 Unauthorized`

```json
{
  "error": {
    "code": "BANK_TOKEN_EXPIRED",
    "message": "Your connected bank account needs to be re-authorized before you can request a payout.",
    "details": {
      "connection_id": "bankconn_8f3kd0",
      "reason": "token_expired",
      "reconnect_url": "/settings/bank-connections/bankconn_8f3kd0/reconnect"
    },
    "request_id": "req_01HZX9Q2K7..."
  }
}
```

Why these fields:
- `reconnect_url` gives the client a direct path to remediation so it can render a "Reconnect your bank" button without hard-coding routes.
- `connection_id` identifies *which* connection expired when a user has more than one.

### 2. Amount exceeds daily payout limit — `422 Unprocessable Entity`

```json
{
  "error": {
    "code": "PAYOUT_LIMIT_EXCEEDED",
    "message": "This payout exceeds your remaining daily limit.",
    "details": {
      "currency": "GBP",
      "requested_amount": 1500.00,
      "daily_limit": 2000.00,
      "used_today": 1200.00,
      "remaining_today": 800.00,
      "limit_resets_at": "2026-06-04T00:00:00Z"
    },
    "request_id": "req_01HZX9R5M1..."
  }
}
```

Why these fields:
- Returning `daily_limit`, `used_today`, and `remaining_today` lets the UI say exactly "You can send up to GBP 800.00 more today" with no extra round trip.
- `limit_resets_at` lets the client tell the user when they can try again.
- Money is shown here as decimals for readability; **in real code prefer integer minor units** (e.g. `"requested_amount": 150000` for £1,500.00) plus the `currency` code, to avoid floating-point rounding. Keep this consistent with how amounts are represented in the request body.

### 3. Sequra (payment provider) rejects the payout — `502 Bad Gateway`

```json
{
  "error": {
    "code": "PROVIDER_REJECTED",
    "message": "We couldn't process this payout right now. Please try again shortly.",
    "details": {
      "provider": "sequra",
      "provider_error_code": "SQ-4012",
      "provider_message": "Risk check failed for beneficiary account",
      "retryable": true
    },
    "request_id": "req_01HZX9T8N9..."
  }
}
```

Why this shape:
- The top-level `code` is **your** stable contract (`PROVIDER_REJECTED`), not Sequra's. If you migrate off Sequra, clients that branch on `code` keep working.
- The raw vendor specifics live under `details.provider*` purely for logging/support, clearly namespaced so nobody mistakes `SQ-4012` for a value they should switch on in production.
- `retryable` tells the client whether a retry is worth attempting. Map this from the provider's error class on your side rather than making clients learn Sequra's taxonomy.
- The user-facing `message` stays generic and reassuring — never pass the raw provider message straight to the end user, as it may be confusing or leak internal detail.

---

## Notes for implementation

- **Centralize this.** Define a single `apiError(code, status, message, details?)` helper (or a small error class) and a typed union of allowed `code`s so every route — `payouts` and beyond — emits the identical envelope. Don't hand-build response objects per route.
- **Always set `request_id`** from your request context / logging middleware and log it alongside the full provider response, so a user reporting "payout failed" can be traced to the exact upstream call.
- **Validation errors** (bad/missing fields in the request) are a separate, earlier case — typically `400` with `code: "VALIDATION_ERROR"` and a `details.fields` array. Worth defining now so the limit case (a *business* rule, `422`) stays cleanly distinct from *schema* validation (`400`).
- **Document the `code` catalogue.** The set of `code` strings is a public contract; list them (with their HTTP status and whether they're retryable) in your API docs.

### Minimal TypeScript sketch (App Router)

```ts
type ErrorCode =
  | "BANK_TOKEN_EXPIRED"
  | "PAYOUT_LIMIT_EXCEEDED"
  | "PROVIDER_REJECTED"
  | "VALIDATION_ERROR";

function apiError(
  status: number,
  code: ErrorCode,
  message: string,
  details?: Record<string, unknown>,
) {
  return Response.json(
    { error: { code, message, details, request_id: getRequestId() } },
    { status },
  );
}

// usage
return apiError(422, "PAYOUT_LIMIT_EXCEEDED", "This payout exceeds your remaining daily limit.", {
  currency: "GBP",
  requested_amount: 150000,
  daily_limit: 200000,
  remaining_today: 80000,
  limit_resets_at: "2026-06-04T00:00:00Z",
});
```

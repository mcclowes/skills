# `POST /api/v1/payouts` — error response design

Every non-success response from this endpoint carries a single top-level `issues` array. Errors, warnings, and informational notices all use the same shape and the same location, so a client only ever has to look in one place to find out what happened, trace it, and decide what to do next.

## The three failure cases

| Case | HTTP status | `type` | `issue` | Notes |
|---|---|---|---|---|
| Connected bank token expired | `401 Unauthorized` | `unauthorized` | `unauthorized.bank_token_expired` | Stateful — `active: true` until the user re-authorises the bank connection. |
| Amount exceeds daily payout limit | `422 Unprocessable Entity` | `validation` | `validation.daily_limit_exceeded` | Carries machine-readable context (limit, remaining) so the client can show the user a real number. |
| Sequra (payment provider) rejection | `502 Bad Gateway` | `internal` | `internal.provider_rejected` | Wraps Sequra's own code/message verbatim in `thirdParty`. The client keys off our `issue`, never Sequra's code. |

A few design choices worth calling out:

- **Descriptive, namespaced string codes** (`validation.daily_limit_exceeded`), never numeric ones. A developer reads it and knows what happened without a lookup table. We keep `issue` a plain string (not a strict enum) so the taxonomy can grow without breaking consumers — tell integrators to handle unknown values gracefully.
- **`type` stays category-level.** The Sequra rejection is categorised as `internal` because, from the client's perspective, our service failed to complete the payout via our upstream — the detail of *who* failed lives in `issue` and `thirdParty`, not in a proliferating set of top-level types.
- **`correlationId` on every response.** Generated per request; if the client sends `X-Correlation-ID`, we echo it back so they can line their logs up with ours.
- **`active` only where we genuinely track resolution state.** The expired bank token is `active: true` (it stays broken until re-auth), so we include it. The limit and provider cases are point-in-time, so we omit `active` rather than emit a meaningless value.
- **`message` is end-user-safe, English-only convenience copy.** The integrator can override it and owns localisation.
- **`thirdParty` is opaque passthrough.** We forward Sequra's `provider`/`code`/`message` unchanged, assume it's *not* fit to show end users, and never branch logic on it.

## Case 1 — Bank token expired (`401`)

```json
{
  "issues": [
    {
      "type": "unauthorized",
      "issue": "unauthorized.bank_token_expired",
      "severity": "error",
      "correlationId": "4b3a2c1d-9f8e-4a7b-bc12-abcdef123456",
      "dateTime": "2026-06-03T09:14:22Z",
      "active": true,
      "message": {
        "title": "Bank connection expired",
        "detail": "We can't access your bank account because the connection has expired. Please reconnect your bank to continue."
      },
      "links": {
        "documentation": "https://docs.example.com/errors/unauthorized.bank_token_expired",
        "portal": "https://support.example.com",
        "api": "https://api.example.com/api/v1/bank-connections/reauthorize"
      }
    }
  ]
}
```

`active: true` signals the connection is still broken; the client can treat it as an ongoing condition until re-auth. `links.api` points at the re-authorisation endpoint — the concrete next action.

## Case 2 — Daily payout limit exceeded (`422`)

```json
{
  "issues": [
    {
      "type": "validation",
      "issue": "validation.daily_limit_exceeded",
      "severity": "error",
      "correlationId": "7d2f1a9c-3b6e-4c80-9a11-0123456789ab",
      "dateTime": "2026-06-03T09:15:03Z",
      "message": {
        "title": "Daily payout limit reached",
        "detail": "This payout would exceed your daily limit of £5,000. You have £1,200 remaining today. Try a smaller amount or wait until tomorrow."
      },
      "context": {
        "requestedAmount": 3500,
        "dailyLimit": 5000,
        "remainingToday": 1200,
        "currency": "GBP"
      },
      "links": {
        "documentation": "https://docs.example.com/errors/validation.daily_limit_exceeded",
        "portal": "https://support.example.com",
        "api": "https://api.example.com/api/v1/payout-limits"
      }
    }
  ]
}
```

Note the optional `context` object. It's an additive, issue-specific extension carrying the machine-readable numbers behind the limit, so the client can render a precise message or pre-fill a corrected amount rather than parsing them out of `message.detail`. Amounts are minor-unit-free integers here with an explicit `currency`; match whatever money convention the rest of your API already uses. Because it's purely additive and namespaced under a single issue, adding it doesn't break consumers who ignore it.

## Case 3 — Sequra rejects the payout (`502`)

```json
{
  "issues": [
    {
      "type": "internal",
      "issue": "internal.provider_rejected",
      "severity": "error",
      "correlationId": "e1c4b7a0-5d2f-4e93-8f01-fedcba987654",
      "dateTime": "2026-06-03T09:16:47Z",
      "message": {
        "title": "Payout couldn't be completed",
        "detail": "Your payout couldn't be processed right now. No money has left your account. Please try again shortly or contact support if it keeps happening."
      },
      "thirdParty": {
        "provider": "sequra",
        "code": "PAYOUT_DECLINED_RISK",
        "message": "Payout declined by risk engine: recipient account flagged for manual review."
      },
      "links": {
        "documentation": "https://docs.example.com/errors/internal.provider_rejected",
        "portal": "https://support.example.com",
        "api": "https://api.example.com/api/v1/payouts/po_01HXYZ/retry"
      }
    }
  ]
}
```

The `thirdParty` block is Sequra's raw output, passed through untouched. The client surfaces our `message` to the end user (Sequra's wording isn't user-safe and may leak internal detail), uses `thirdParty` only for logging and support escalation, and branches application logic exclusively on our `issue` value. `links.api` points at a retry endpoint for this specific payout.

## Multiple issues at once

The container is an array on purpose. If a single request trips more than one condition — say validation surfaces several field problems, or an `error` ships alongside an advisory `warning` — they all appear in the same `issues` array, ordered most significant first. Clients should iterate, key off `issue`, and act on `severity` (`error` = failed, action required; `warning` = succeeded with caveats; `info` = advisory).

## TypeScript shape (for the consuming side)

```ts
type Severity = "error" | "warning" | "info";

interface Issue {
  type: "unauthorized" | "validation" | "conflict" | "rate_limit" | "internal";
  issue: string; // namespaced `{type}.{detail}` — treat as open string, handle unknowns
  severity: Severity;
  correlationId: string;
  dateTime: string; // ISO 8601 UTC
  active?: boolean;
  message?: { title: string; detail: string };
  thirdParty?: { provider: string; code?: string; message?: string };
  context?: Record<string, unknown>; // additive, issue-specific
  links?: { documentation?: string; portal?: string; api?: string };
}

interface ErrorResponse {
  issues: Issue[];
}
```

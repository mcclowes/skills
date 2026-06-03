# Unifying error handling across REST responses and webhooks

## The core problem

Right now you have two divergent failure shapes. Your REST API fails one way, your webhooks fail another, and your React frontend pays the tax: every place that touches a failure has to know which source it came from and branch accordingly. That branching multiplies with every new endpoint or event type.

The fix isn't to reconcile two formats — it's to adopt **one** failure shape and emit it everywhere a failure, warning, or notice is surfaced: REST response bodies, webhook payloads, and any future callbacks. A failure is a failure regardless of transport. The frontend should be able to consume it through a single code path.

## The unified shape: one `issues` array

Every non-success outcome carries a single `issues` array. Errors, warnings, and informational notices share one shape and one location, because they share one need: context, traceability, and a path forward. Splitting errors and warnings into separate fields (or separate REST-vs-webhook formats) forces consumers to check multiple places for information that belongs to the same moment.

Each issue object uses these fields:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `type` | enum string | Yes | Top-level category (`unauthorized`, `validation`, `conflict`, `rate_limit`, `internal`, …) |
| `issue` | namespaced string | Yes | Specific machine-readable code, `{type}.{detail}`, e.g. `validation.missing_field` |
| `severity` | enum string | Yes | `error` (failed, action required), `warning` (succeeded, attention advised), `info` |
| `correlationId` | UUID string | Yes | Unique per request/event; the fastest way to find it in logs |
| `dateTime` | ISO 8601 string | Yes | When the issue occurred, in UTC |
| `active` | boolean | No | Whether the issue is still ongoing; omit if you can't track it reliably |
| `message` | object | No | `{ title, detail }` human-readable copy, safe to surface to end users |
| `thirdParty` | object | No | `{ provider, code, message }` passed through verbatim from an upstream service |
| `links` | object | No | `{ documentation, portal, api }` to help the developer act |

A few rules that are easy to get wrong:

- **Descriptive string codes, not numeric ones.** `validation.missing_field` is self-explanatory; `4012` needs a lookup table.
- **Namespace `issue` as `{type}.{detail}`** so related codes read as related.
- **Keep `issue` a plain string, not a strict enum.** The taxonomy grows; a strict enum makes every new code a breaking change. Tell consumers to tolerate unknown values.
- **Always generate a `correlationId`**, and if the caller sends `X-Correlation-ID`, echo it back.
- **Omit `active` rather than lie.** A stale `active: true` is worse than no signal.

## The key insight for webhooks: the issue payload is identical, only the envelope differs

A REST response and a webhook are delivered differently, but the *failure description* should be byte-for-byte the same object. So:

- The `issues` array and the objects inside it are **identical** across both transports.
- The webhook wraps that array in a thin event envelope (`event`, `eventId`, `resource`) carrying delivery metadata that a synchronous response doesn't need. The frontend can ignore the envelope entirely and hand the `issues` array to the same handler it uses for REST.

This is what lets you delete the special-casing: a single `handleIssues(issues, correlationId)` function consumes both.

### REST error response

`POST /payments` → `402 Payment Required`

```json
{
  "correlationId": "4b3a2c1d-0000-0000-0000-abcdef123456",
  "issues": [
    {
      "type": "unauthorized",
      "issue": "unauthorized.payment_declined",
      "severity": "error",
      "correlationId": "4b3a2c1d-0000-0000-0000-abcdef123456",
      "dateTime": "2026-06-03T12:34:56Z",
      "message": {
        "title": "Payment not authorised",
        "detail": "This transaction couldn't be completed. Please check your card details or contact support."
      },
      "thirdParty": {
        "provider": "acme_payments",
        "code": "DECLINED_INSUFFICIENT_FUNDS",
        "message": "The card was declined due to insufficient funds."
      },
      "links": {
        "documentation": "https://docs.example.com/errors/unauthorized",
        "portal": "https://support.example.com",
        "api": "https://api.example.com/payments/123/retry"
      }
    }
  ]
}
```

### Webhook failure delivery — same `issues`, thin envelope

`POST` to the subscriber's webhook URL:

```json
{
  "event": "payment.failed",
  "eventId": "evt_8f2b91c4",
  "dateTime": "2026-06-03T12:34:58Z",
  "resource": {
    "type": "payment",
    "id": "pay_123"
  },
  "correlationId": "4b3a2c1d-0000-0000-0000-abcdef123456",
  "issues": [
    {
      "type": "unauthorized",
      "issue": "unauthorized.payment_declined",
      "severity": "error",
      "correlationId": "4b3a2c1d-0000-0000-0000-abcdef123456",
      "dateTime": "2026-06-03T12:34:56Z",
      "message": {
        "title": "Payment not authorised",
        "detail": "This transaction couldn't be completed. Please check your card details or contact support."
      },
      "thirdParty": {
        "provider": "acme_payments",
        "code": "DECLINED_INSUFFICIENT_FUNDS",
        "message": "The card was declined due to insufficient funds."
      },
      "links": {
        "documentation": "https://docs.example.com/errors/unauthorized",
        "portal": "https://support.example.com",
        "api": "https://api.example.com/payments/123/retry"
      }
    }
  ]
}
```

The `issues[0]` object is identical in both. Note how `correlationId` ties the webhook back to the original request — the same value appears in the REST response, the webhook envelope, and your server logs, so a single ID stitches the whole story together.

### Webhooks also benefit from `active` and `warning`

Webhooks often describe stateful, ongoing conditions where the REST response is just a point-in-time failure. This is exactly where `active` and `severity: warning` earn their keep. A degraded-but-succeeded outcome:

```json
{
  "event": "device.status_changed",
  "eventId": "evt_a1b2c3d4",
  "dateTime": "2026-06-03T13:00:00Z",
  "resource": { "type": "device", "id": "dev_77" },
  "correlationId": "9c8b7a6d-1111-2222-3333-444455556666",
  "issues": [
    {
      "type": "internal",
      "issue": "internal.device_offline",
      "severity": "warning",
      "correlationId": "9c8b7a6d-1111-2222-3333-444455556666",
      "dateTime": "2026-06-03T13:00:00Z",
      "active": true,
      "message": {
        "title": "Device offline",
        "detail": "The device stopped responding and will reconnect automatically. No action needed unless it persists."
      }
    }
  ]
}
```

When the device reconnects, you emit the same event with `"active": false` so the consumer can clear the condition. Only include `active` where you genuinely track resolution state.

## Consuming the unified shape in React

Because the issue object is identical across transports, the frontend needs **one** type and **one** handler. The REST client and the webhook channel (e.g. a WebSocket/SSE bridge, or your backend forwarding webhook events to the browser) both feed the same function.

### Shared types

```tsx
type IssueSeverity = 'error' | 'warning' | 'info'

type IssueType =
  | 'unauthorized'
  | 'validation'
  | 'conflict'
  | 'rate_limit'
  | 'internal'

interface IssueMessage {
  title: string
  detail: string
}

interface IssueLinks {
  documentation?: string
  portal?: string
  api?: string
}

interface IssueThirdParty {
  provider: string
  code?: string
  message?: string
}

interface Issue {
  type: IssueType
  issue: string // plain string, not a union — tolerate unknown codes as the taxonomy grows
  severity: IssueSeverity
  correlationId: string
  dateTime: string
  active?: boolean
  message?: IssueMessage
  links?: IssueLinks
  thirdParty?: IssueThirdParty
}

// REST response carries issues directly
interface ApiResponse {
  correlationId: string
  issues?: Issue[]
}

// Webhook event wraps the same issues in a thin envelope
interface WebhookEvent {
  event: string
  eventId: string
  dateTime: string
  resource: { type: string; id: string }
  correlationId: string
  issues?: Issue[]
}
```

### One normalizer, two sources

The only transport-specific code is a tiny adapter that extracts `issues` from each envelope. Everything downstream is shared.

```tsx
function issuesFromResponse(data: ApiResponse): Issue[] {
  return data.issues ?? []
}

function issuesFromWebhook(event: WebhookEvent): Issue[] {
  return event.issues ?? []
}
```

### A single handler both sources call

```tsx
import { useState, useEffect } from 'react'

function useIssueHandler() {
  const [issues, setIssues] = useState<Issue[]>([])
  const [correlationId, setCorrelationId] = useState<string | null>(null)

  // The ONE entry point. REST and webhooks both call this.
  function handleIssues(incoming: Issue[], correlationId: string) {
    if (!incoming.length) return

    // Drop resolved stateful issues (e.g. device came back online).
    const live = incoming.filter((i) => i.active !== false)

    // Cross-cutting handling lives in one place, not per-call-site.
    const unauthorized = live.find((i) => i.type === 'unauthorized')
    if (unauthorized) {
      redirectToLogin({ reason: unauthorized.message?.title, ref: correlationId })
      return
    }

    setIssues(live)
    setCorrelationId(correlationId)
  }

  return { issues, correlationId, handleIssues }
}
```

### Wiring REST and the webhook channel to the same handler

```tsx
export default function App() {
  const { issues, correlationId, handleIssues } = useIssueHandler()

  // --- REST source ---
  async function makePayment() {
    const cid = crypto.randomUUID()
    const res = await fetch('/api/payments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': cid,
      },
      body: JSON.stringify({ amount: 1000, currency: 'GBP' }),
    })
    const data: ApiResponse = await res.json()
    if (!res.ok) {
      handleIssues(issuesFromResponse(data), data.correlationId ?? cid)
    }
  }

  // --- Webhook source (forwarded to the browser via SSE/WebSocket) ---
  useEffect(() => {
    const stream = new EventSource('/api/events')
    stream.onmessage = (e) => {
      const event: WebhookEvent = JSON.parse(e.data)
      handleIssues(issuesFromWebhook(event), event.correlationId)
    }
    return () => stream.close()
  }, [handleIssues])

  return (
    <div>
      <button onClick={makePayment}>Pay</button>
      <IssueList issues={issues} correlationId={correlationId} />
    </div>
  )
}
```

### One rendering component for both

Because everything is normalized to `Issue[]`, a single component renders failures regardless of origin. Severity — not transport — drives presentation.

```tsx
function IssueList({
  issues,
  correlationId,
}: {
  issues: Issue[]
  correlationId: string | null
}) {
  const errors = issues.filter((i) => i.severity === 'error')
  const warnings = issues.filter((i) => i.severity === 'warning')

  return (
    <div>
      {errors.map((issue, idx) => (
        <div key={idx} role="alert">
          {/* Fall back to the machine code when message copy is absent */}
          <strong>{issue.message?.title ?? issue.issue}</strong>
          <p>{issue.message?.detail}</p>
          {issue.links?.documentation && (
            <a href={issue.links.documentation}>Find out more</a>
          )}
        </div>
      ))}

      {warnings.map((issue, idx) => (
        <div key={idx} role="status">
          <strong>{issue.message?.title ?? issue.issue}</strong>
          <p>{issue.message?.detail}</p>
        </div>
      ))}

      {correlationId && <small>Reference: {correlationId}</small>}
    </div>
  )
}
```

`role="alert"` vs `role="status"` mirrors the `error`/`warning` split for assistive tech. The frontend no longer knows or cares whether an issue arrived via REST or webhook — that distinction has been deleted from the consumer.

## Migration path (additive, non-breaking)

Don't break existing consumers. Evolve toward the unified shape:

1. **Add `issues` alongside the current fields** in both REST responses and webhook payloads. Don't remove the old fields yet.
2. **Make the issue object identical** in both transports; let the webhook keep only its envelope metadata (`event`, `eventId`, `resource`) as extra.
3. **Always populate `correlationId`** end to end — request, response, webhook, logs — so the same ID stitches the whole flow together.
4. **Migrate the frontend** to the single `handleIssues` path and delete the per-source branching.
5. **Deprecate and eventually remove** the legacy fields once consumers have moved, communicated via your normal versioning.

Because `issue` stays a plain string and new `type` values are added rather than reshaping the envelope, the taxonomy can keep growing without further breaking changes.

## Why this works — the principles behind it

- **The client can see what happened** — no mystery failures, in either transport.
- **The client can understand why and how to resolve it** — `links` to docs, support, and related resources travel with every issue.
- **The client can relay the issue to their own user** — `message.title`/`message.detail` are end-user-safe copy.
- **No forced change management** — the design is additive; `issue` is a string, not a brittle enum.
- **Resolution state is captured where it matters** — `active` shines in webhooks for ongoing conditions.
- **The shape is consistent across contexts** — that consistency is precisely what collapses the frontend's two code paths into one.
- **It's clear where action is required** — `severity` drives whether the UI alarms or merely informs, independent of where the issue came from.

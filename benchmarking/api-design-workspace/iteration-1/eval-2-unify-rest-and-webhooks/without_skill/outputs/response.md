# Unifying error handling across REST responses and webhooks

## The core problem

Your REST API and your webhooks are two different *transports* for the same underlying concept: "something failed, and here is the structured reason." Today they emit that concept in two different shapes, so the frontend has to special-case each one. The fix is not to make the frontend smarter — it's to define **one canonical error object** on the backend and reuse it everywhere.

The key insight: a REST error and a webhook failure differ only in their *envelope* (how the payload is wrapped and delivered), not in the *error itself*. So separate the two:

- **Error object** — the shape that describes *what went wrong*. Identical everywhere.
- **Envelope** — the transport-specific wrapper (HTTP status + body for REST, event metadata + signature for webhooks).

If the error object is byte-for-byte identical in both places, the frontend needs exactly one parser and one set of UI components.

## The canonical error object

Adopt a single schema, loosely modeled on [RFC 9457 (Problem Details)](https://www.rfc-editor.org/rfc/rfc9457). Every error your system produces — whether returned synchronously from REST or delivered later via webhook — uses this shape:

```json
{
  "error": {
    "type": "https://errors.example.com/payment/card_declined",
    "code": "card_declined",
    "title": "Card was declined",
    "detail": "The card issuer declined the charge for insufficient funds.",
    "status": 402,
    "retryable": false,
    "fields": [
      { "name": "payment.card", "issue": "declined", "message": "Insufficient funds" }
    ],
    "request_id": "req_8f3a2b1c9d",
    "timestamp": "2026-06-03T14:22:01.123Z",
    "docs_url": "https://docs.example.com/errors/card_declined"
  }
}
```

Field-by-field rationale:

| Field | Purpose |
|---|---|
| `type` | Stable URI identifying the error category. Good for dedupe/grouping and docs linking. |
| `code` | Short machine-readable slug (`card_declined`). **This is what the frontend switches on**, never the human strings. |
| `title` | Short, human-readable, stable summary safe to show or log. |
| `detail` | Longer human explanation for *this occurrence*. May be safe to surface to users or only to support. |
| `status` | The HTTP status it maps to. Present even in webhooks so consumers have a consistent severity signal. |
| `retryable` | Boolean telling the client whether retrying could succeed. Removes guesswork from `4xx` vs `5xx`. |
| `fields` | Optional per-field validation errors, so forms can attach messages inline. |
| `request_id` | Correlation ID for support and tracing. |
| `timestamp` | When the error occurred (ISO 8601). |
| `docs_url` | Optional deep link to documentation. |

One enum of `code` values, defined once and shared between REST and webhook producers, is the linchpin. Document it and treat additions as part of your API contract.

## How each transport wraps it

### REST response

The error object goes straight in the body; the HTTP status mirrors `error.status`.

```http
HTTP/1.1 402 Payment Required
Content-Type: application/json
X-Request-Id: req_8f3a2b1c9d
```

```json
{
  "error": {
    "type": "https://errors.example.com/payment/card_declined",
    "code": "card_declined",
    "title": "Card was declined",
    "detail": "The card issuer declined the charge for insufficient funds.",
    "status": 402,
    "retryable": false,
    "fields": [],
    "request_id": "req_8f3a2b1c9d",
    "timestamp": "2026-06-03T14:22:01.123Z",
    "docs_url": "https://docs.example.com/errors/card_declined"
  }
}
```

### Webhook delivery

The webhook has its own envelope (event id, type, signature headers, the resource it concerns) but the failure detail is **the exact same `error` object**, nested unchanged:

```json
{
  "id": "evt_01HZX9K2QF",
  "type": "payment.failed",
  "created": "2026-06-03T14:22:01.456Z",
  "api_version": "2026-06-01",
  "data": {
    "object": {
      "id": "pay_5521",
      "amount": 4900,
      "currency": "usd",
      "status": "failed"
    }
  },
  "error": {
    "type": "https://errors.example.com/payment/card_declined",
    "code": "card_declined",
    "title": "Card was declined",
    "detail": "The card issuer declined the charge for insufficient funds.",
    "status": 402,
    "retryable": false,
    "fields": [],
    "request_id": "req_8f3a2b1c9d",
    "timestamp": "2026-06-03T14:22:01.123Z",
    "docs_url": "https://docs.example.com/errors/card_declined"
  }
}
```

Note the deliberate split:
- `error.timestamp` / `error.request_id` describe **when the failure happened** (the original operation).
- `created` / `id` on the envelope describe **when the webhook event was emitted**. These are different moments and you want both.

Because the inner `error` object is identical to what REST returns, the frontend reuses the same parsing and rendering logic for both.

## Backend: produce it once

Define the error type and a single factory, then have both the HTTP layer and the webhook emitter call it. Below in TypeScript.

```ts
// errors/types.ts
export type FieldError = {
  name: string;
  issue: string;
  message: string;
};

export type ApiError = {
  type: string;
  code: string;
  title: string;
  detail: string;
  status: number;
  retryable: boolean;
  fields: FieldError[];
  request_id: string;
  timestamp: string;
  docs_url?: string;
};
```

```ts
// errors/catalog.ts
// Single source of truth: every error code lives here, shared by REST + webhooks.
type ErrorDef = {
  status: number;
  title: string;
  retryable: boolean;
};

export const ERROR_CATALOG = {
  card_declined: { status: 402, title: "Card was declined", retryable: false },
  rate_limited: { status: 429, title: "Too many requests", retryable: true },
  validation_failed: { status: 422, title: "Validation failed", retryable: false },
  internal_error: { status: 500, title: "Something went wrong", retryable: true },
} satisfies Record<string, ErrorDef>;

export type ErrorCode = keyof typeof ERROR_CATALOG;
```

```ts
// errors/build.ts
import { ApiError, FieldError } from "./types";
import { ERROR_CATALOG, ErrorCode } from "./catalog";

const DOCS_BASE = "https://docs.example.com/errors";
const TYPE_BASE = "https://errors.example.com";

export function buildError(
  code: ErrorCode,
  opts: {
    detail: string;
    requestId: string;
    fields?: FieldError[];
    timestamp?: string;
  }
): ApiError {
  const def = ERROR_CATALOG[code];
  return {
    type: `${TYPE_BASE}/${code}`,
    code,
    title: def.title,
    detail: opts.detail,
    status: def.status,
    retryable: def.retryable,
    fields: opts.fields ?? [],
    request_id: opts.requestId,
    timestamp: opts.timestamp ?? new Date().toISOString(),
    docs_url: `${DOCS_BASE}/${code}`,
  };
}
```

REST handler (Express-style):

```ts
import { buildError } from "../errors/build";

app.post("/payments", async (req, res) => {
  try {
    const payment = await chargeCard(req.body);
    res.status(201).json({ data: payment });
  } catch (e) {
    if (e instanceof CardDeclinedError) {
      const error = buildError("card_declined", {
        detail: e.message,
        requestId: req.id,
      });
      // HTTP status mirrors the error object — single source of truth.
      return res.status(error.status).json({ error });
    }
    const error = buildError("internal_error", {
      detail: "Unexpected error",
      requestId: req.id,
    });
    res.status(error.status).json({ error });
  }
});
```

Webhook emitter — reuses the same `buildError`, just wraps it differently:

```ts
import { buildError } from "../errors/build";

async function emitPaymentFailed(payment: Payment, requestId: string) {
  const error = buildError("card_declined", {
    detail: "The card issuer declined the charge for insufficient funds.",
    requestId,
    timestamp: payment.failedAt, // when the failure actually occurred
  });

  const event = {
    id: generateEventId(),
    type: "payment.failed",
    created: new Date().toISOString(),
    api_version: "2026-06-01",
    data: { object: serializePayment(payment) },
    error, // same object, unchanged
  };

  await deliverWebhook(event); // adds signature headers, retries, etc.
}
```

## Frontend: one parser, one set of components

Because the inner shape is identical, you write the error logic **once** and feed it from either source.

```ts
// lib/apiError.ts
export type FieldError = { name: string; issue: string; message: string };

export type ApiError = {
  type: string;
  code: string;
  title: string;
  detail: string;
  status: number;
  retryable: boolean;
  fields: FieldError[];
  request_id: string;
  timestamp: string;
  docs_url?: string;
};

// Type guard: accepts the inner object from EITHER a REST body or a webhook event.
export function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === "object" &&
    value !== null &&
    typeof (value as ApiError).code === "string" &&
    typeof (value as ApiError).status === "number"
  );
}

// Normalizes both sources to the same ApiError | null.
export function extractError(payload: unknown): ApiError | null {
  if (typeof payload !== "object" || payload === null) return null;
  const maybe = (payload as { error?: unknown }).error;
  return isApiError(maybe) ? maybe : null;
}
```

A small fetch wrapper that throws a typed error:

```ts
// lib/apiClient.ts
import { ApiError, extractError } from "./apiError";

export class ApiErrorException extends Error {
  constructor(public readonly apiError: ApiError) {
    super(apiError.title);
    this.name = "ApiErrorException";
  }
}

export async function apiFetch<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const res = await fetch(input, init);
  const body = await res.json().catch(() => null);

  if (!res.ok) {
    const apiError = extractError(body);
    if (apiError) throw new ApiErrorException(apiError);
    throw new Error(`Request failed with status ${res.status}`);
  }
  return body as T;
}
```

A single presentational component, driven only by `code` / `retryable` / `fields`:

```tsx
// components/ErrorBanner.tsx
import { ApiError } from "../lib/apiError";

export function ErrorBanner({
  error,
  onRetry,
}: {
  error: ApiError;
  onRetry?: () => void;
}) {
  return (
    <div role="alert" className="error-banner" data-code={error.code}>
      <strong>{error.title}</strong>
      <p>{error.detail}</p>

      {error.fields.length > 0 && (
        <ul>
          {error.fields.map((f) => (
            <li key={f.name}>
              <code>{f.name}</code>: {f.message}
            </li>
          ))}
        </ul>
      )}

      {error.retryable && onRetry && (
        <button onClick={onRetry}>Try again</button>
      )}

      {error.docs_url && (
        <a href={error.docs_url} target="_blank" rel="noreferrer">
          Learn more
        </a>
      )}

      <small className="error-meta">Reference: {error.request_id}</small>
    </div>
  );
}
```

### Consuming a REST error

```tsx
import { useState } from "react";
import { apiFetch, ApiErrorException } from "../lib/apiClient";
import { ApiError } from "../lib/apiError";
import { ErrorBanner } from "../components/ErrorBanner";

export function PaymentForm() {
  const [error, setError] = useState<ApiError | null>(null);

  async function submit(payload: unknown) {
    setError(null);
    try {
      await apiFetch("/payments", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    } catch (e) {
      if (e instanceof ApiErrorException) setError(e.apiError);
      else throw e;
    }
  }

  return (
    <form onSubmit={/* ... */ undefined}>
      {error && <ErrorBanner error={error} onRetry={() => submit({})} />}
      {/* fields... */}
    </form>
  );
}
```

### Consuming a webhook-driven error

Webhooks are delivered to your *server*, not the browser, so the frontend usually learns about them over a realtime channel (WebSocket, SSE, or by polling a notifications endpoint). Whatever the channel, you reuse the exact same `extractError` and `ErrorBanner` — that is the whole payoff.

```tsx
// hooks/usePaymentEvents.ts
import { useEffect, useState } from "react";
import { ApiError, extractError } from "../lib/apiError";

export function usePaymentEvents() {
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    const source = new EventSource("/events/stream");
    source.addEventListener("payment.failed", (e) => {
      const event = JSON.parse((e as MessageEvent).data);
      // Same extractor as REST — the inner `error` shape is identical.
      setError(extractError(event));
    });
    return () => source.close();
  }, []);

  return error;
}
```

```tsx
// components/PaymentStatus.tsx
import { usePaymentEvents } from "../hooks/usePaymentEvents";
import { ErrorBanner } from "./ErrorBanner";

export function PaymentStatus() {
  const error = usePaymentEvents();
  if (!error) return <p>Payment processing…</p>;
  // Exact same component used for REST errors.
  return <ErrorBanner error={error} />;
}
```

Note there's no `onRetry` here — a webhook failure typically isn't something the user re-submits inline. But `ErrorBanner` handles both cases because it keys off `error.retryable` and the presence of a handler, not off where the error came from.

## Migration path (without breaking existing consumers)

1. **Define the catalog and `buildError` first.** Lock down the `code` enum and publish it as part of your API docs.
2. **Add the new shape alongside the old one.** For REST, you can emit both the legacy fields and the new `error` object during a deprecation window; for webhooks, add the `error` key without removing existing failure fields.
3. **Migrate the frontend** to `extractError` + `ErrorBanner`, falling back to the legacy parser if `error` is absent.
4. **Version webhooks** via the `api_version` field so old subscribers keep their shape until they opt in.
5. **Remove legacy fields** once telemetry shows no consumers rely on them.

## Why this is the right shape

- **One contract, two envelopes.** The error object is transport-agnostic; only the wrapper differs. That's the minimum necessary difference.
- **Machine-readable `code` is the contract; human strings are not.** The frontend never branches on `title`/`detail`, so you can reword them freely without breaking clients.
- **`retryable` and `status` travel with the error** so consumers don't reverse-engineer behavior from HTTP semantics that don't even exist in a webhook.
- **`request_id` everywhere** makes support and tracing uniform regardless of how the error surfaced.
- **The frontend collapses to one parser and one component**, which is exactly the special-casing you wanted to eliminate.

A reasonable simpler alternative if RFC 9457 feels heavy: drop `type` and `docs_url` and keep just `code`, `title`, `detail`, `status`, `retryable`, `fields`, `request_id`, `timestamp`. The unification benefit comes entirely from *sharing the object between transports* — the exact field list is secondary, so don't over-engineer it.

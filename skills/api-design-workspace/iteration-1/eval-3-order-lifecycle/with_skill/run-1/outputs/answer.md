# Modelling the order lifecycle: status, events, and issues

The core problem is that your single `status` string is being asked three different questions at once, and `payment_failed` is where that overload becomes visible. The frontend has to special-case it because `payment_failed` is trying to be a *state*, an *event*, and an *error reason* all in one word — and it isn't really any of them. It's the last thing that happened, smuggled into the field that's supposed to say where the order is now.

The fix is to split that one field into three carriers, each answering one question:

- **What just happened?** → an **event** (past-tense verb, on the webhook envelope) — `order.payment_failed`
- **Where is the order now?** → the **status** (one persistent value, driven by a state machine) — `order.unpaid`
- **Why, and what should the user do?** → an **issue** (a structured annotation, with severity, message, and links) — `payment.declined.insufficient_funds`

Once you do this, `payment_failed` stops being a status at all, and the frontend's special-casing disappears.

## Why `payment_failed` is the wrong status

A status should name the **present condition** of the resource — what the order *is* right now, not what just happened to it and not what someone needs to do next. `payment_failed` fails this test in two ways:

1. **It names the last event, echoed back.** "Failed" describes a transition that completed, not a condition the order is in. The order isn't *in a failed state* — it's an order that still hasn't been paid for, exactly as it was before the attempt. The tell is that the natural name collides with the event (`payment_failed` the thing-that-happened vs `payment_failed` the status). That collision is a diagnostic: it means you've recorded *what happened* in the field meant for *where you are*.

2. **It treats failure as terminal.** Listing `payment_failed` as a sibling of `paid`/`shipped`/`delivered` makes it look like an exit, a dead end. But a failed payment can be retried — it's a detour, not a destination. The state space needs to *loop back* so a retry is just a normal transition, not a special escape from a failure state.

Both problems vanish if a failed payment simply returns the order to **`unpaid`**. That's the same value whether it's the first attempt or the fourth — failure loops back. The reason it failed, and whether they can try again, lives in the issue, not the status.

## The state machine

Draw the machine before naming anything. Nodes are states (present conditions), edges are transitions (events).

```
                  created/checkout
        [*] ──────────────────────────▶ unpaid
                                          │  ▲
                            submitted     │  │  declined / recoverable
                                          ▼  │
                                      processing
                                       │      │
                            captured   │      │  declined / retry limit reached
                                       ▼      ▼
                                     paid    canceled  ──▶ [*]
                                       │
                            shipped    │
                                       ▼
                                    shipped
                                       │
                            delivered  │
                                       ▼
                                   delivered ──▶ [*]
```

Note what the diagram forces into the open:

- **A failed payment has two edges, not one.** Back to `unpaid` when the buyer can retry; out to `canceled` only when retries are exhausted (or they give up). There is no `payment_failed` node — the failure is an edge, not a state.
- **`processing` is a real, short-lived state** — the system is actively authorising/capturing. This is where the order genuinely *is* between submitting payment and the result landing. It's the one state where `-ing` is honest, because the system is doing work that will finish on its own.
- **Terminal states are only the genuine ends:** `delivered` (success) and `canceled` (explicit end). Failure is never terminal on its own.

### Suggested statuses

Using the `{domain}.{state}` grammar so the status is legible even when it arrives in an aggregated webhook stream without its envelope:

| Status | Present condition | Terminal? |
|---|---|---|
| `order.unpaid` | Created, awaiting (or retrying) payment | No |
| `order.processing` | Payment submitted, system is authorising/capturing | No |
| `order.paid` | Payment captured, not yet shipped | No |
| `order.shipped` | Dispatched, in transit | No |
| `order.delivered` | Received by customer | Yes |
| `order.canceled` | Ended without fulfilment (retries exhausted, or user/merchant canceled) | Yes |

Every name describes what the order *is*, never what just happened (`paid`, not `payment_succeeded`) and never what's owed next (`unpaid`, not `awaiting_payment` or `requires_payment`). Note US spelling — `canceled`, `fulfillment` — because the status code is part of the contract and spelling is part of the identifier.

`created` collapses into `unpaid`: "created" and "unpaid" are the same condition (exists, not yet paid for), so the diagram has nothing distinguishing their transitions. Keep `created` only if a created-but-not-yet-submitted order genuinely has different transitions from one that's bounced back from a failed payment — for most checkouts it doesn't.

## The events

Events are **past-tense verbs**, namespaced to the domain, and they live on the webhook envelope (`event.type`), *not* in the status field. Fire one per transition:

- `order.created`
- `order.payment_submitted`
- `order.paid`
- `order.payment_failed`   ← this is where `payment_failed` legitimately lives
- `order.shipped`
- `order.delivered`
- `order.canceled`

So `payment_failed` doesn't disappear — it moves to where it belongs. It was always describing *what happened*, and an event is the carrier for what happened. The webhook for a failed payment carries `event.type: order.payment_failed`, while the order's `status` is back to `order.unpaid`. Events and statuses can share vocabulary safely because they live in different fields and different namespaces — `event.type` vs `order.status` — so even `order.paid` the event and `order.paid` the status never collide in practice.

## The issue: where "can they retry?" actually lives

This is the part that solves the frontend's real pain. When a payment fails, the *why* and the *what to do* go into an **issue** — the same structured shape you'd use for any error across the API:

```json
{
  "order": {
    "id": "ord_123",
    "status": "order.unpaid"
  },
  "issues": [
    {
      "issue": "payment.declined.insufficient_funds",
      "severity": "error",
      "correlationId": "4b3a2c1d-0000-0000-0000-abcdef123456",
      "dateTime": "2026-06-04T12:34:56Z",
      "message": {
        "title": "Payment didn't go through",
        "detail": "Your card was declined for insufficient funds. Please try a different card."
      },
      "links": {
        "documentation": "https://docs.example.com/errors/payment-declined",
        "api": "https://api.example.com/orders/ord_123/pay"
      }
    }
  ]
}
```

The frontend now reads cleanly without special-casing a status value:

- **Status `order.unpaid`** → "this order isn't paid for, show the pay button."
- **An issue with `severity: error`** → "show the user this message" (use `message.title`/`message.detail`, or override with your own copy).
- **`links.api` present** → "they can retry; wire the retry button to this endpoint." When retries are exhausted, you stop emitting the retry link (and the status moves to `order.canceled`), so its presence *is* the "can they try again?" signal — no separate flag needed.

The "show different copy on the second attempt" requirement falls out for free: it's just a different issue `message`, or the presence of an earlier `order.payment_failed` event in the order's history. You never need an `unpaid.awaiting_retry` substate or a bespoke `last_failure_reason` field — the issue is the one consistent place the *why* lives, the same shape used everywhere else in the API.

### Why this beats what you have

The decline reason (`insufficient_funds`, `card_expired`, `do_not_honor`, …) would have multiplied your status enum into dozens of `payment_failed_*` variants, or forced the frontend to parse a separate reason field anyway. Keeping it in the issue's `{domain}.{class}.{reason}` code means:

- the status stays a small, stable set (good for an enum if you want one);
- the reason can grow freely without touching the status contract;
- the frontend branches on `payment.declined` (the prefix) and treats reasons it doesn't recognise as "more specific than I handle," falling back to the issue's `message` and `severity`.

## Should status be an enum or a parseable string?

Your order status set is small and fairly stable, so a strict enum (`order.unpaid`, `order.processing`, …) is defensible. But the dot-separated string is the safer middle path if you expect to add states (e.g. `order.refunded`, or substates under `processing` like `order.processing.authorizing`): consumers `split('.')` and match prefixes, so `order.processing` code keeps working even if you later add a substate. Whichever you pick, **make the same choice for the issue codes** — don't ship a strict-enum status alongside forgiving-string issue codes. If you go the parseable-string route, document the discipline: match on prefixes, never assume a fixed segment depth.

## One caution to keep the model clean

Don't let the failure reason creep back into the status as a substate (`order.unpaid.payment_failed`). The substate slot is for *where* the order is (`processing.authorizing`), not *why* it got there. The moment a substate starts absorbing failure reasons it's quietly becoming an error field — and that's the issue's job. Keep `unpaid` clean; let the issue carry the cause.

## Summary

| Question | Carrier | Example | Lives in |
|---|---|---|---|
| What happened? | Event | `order.payment_failed` | Webhook `event.type` |
| Where is the order? | Status | `order.unpaid` | `order.status` |
| Why / what now? | Issue | `payment.declined.insufficient_funds` | `issues[]` |

Concretely: delete `payment_failed` as a status value. A failed payment fires the `order.payment_failed` *event*, returns the order to `order.unpaid`, and attaches an *issue* carrying the decline reason, the user-facing copy, and (while retries remain) a retry link. The frontend keys off the status for what to show and off the issue for whether they can try again — no special-casing required.

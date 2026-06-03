---
name: api-design
description: Use when designing, reviewing, or implementing HTTP API responses — error and warning handling, and resource state/lifecycle. Triggers on tasks involving API error responses, error formats, error schemas, response envelopes, webhook payloads, "how should this endpoint fail", reviewing an API's error shape, or making error handling consistent across endpoints. ALSO triggers on modelling a resource's lifecycle: designing or naming a `status` field, building a state machine, naming webhook events, deciding between an enum and a parseable status string, or splitting "what happened" / "where is it" / "why". Apply this whenever an API surfaces a failure, warning, partial success, or state change to a client, even if the user just says "handle errors", "design the response", or "what statuses should this have" without naming a pattern.
license: MIT
metadata:
  author: mcclowes
  version: "1.1.0"
---

# API design

Opinionated patterns for designing developer-friendly HTTP APIs. Two components are developed so far, and they're designed to fit together:

- **Error and warning handling** via a unified `issues` array — see below and [references/error-handling.md](references/error-handling.md).
- **State and events** — modelling a resource's lifecycle, and the split between *what happened* (event), *where the resource is* (status), and *why / what to do* (issue) — see [references/event-status-design.md](references/event-status-design.md).

As more components are added (pagination, versioning, naming), they live alongside these in `references/`.

## When this applies

Reach for this whenever an API needs to communicate that something went wrong, partially succeeded, or warrants attention — in a response body, a webhook, or a component callback. It also applies whenever you're modelling a resource's lifecycle: designing a `status` field, naming webhook events, or building a state machine. The goal is responses a developer can act on without guesswork, and that they can relay to *their* end users.

## The core idea: one `issues` array

Every non-success response carries a single `issues` array. Errors, warnings, and informational notices share one shape and one location, because they share one need — context, traceability, and a path forward. Splitting errors and warnings into separate arrays forces consumers to check two places for information that belongs to the same moment in a request.

```json
{
  "issues": [
    {
      "issue": "payment.unauthorized.token_expired",
      "severity": "error",
      "correlationId": "4b3a2c1d-0000-0000-0000-abcdef123456",
      "dateTime": "2024-11-01T12:34:56Z",
      "active": false,
      "message": {
        "title": "Payment not authorised",
        "detail": "This transaction couldn't be completed. Please check your card details or contact support."
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

## Why it's shaped this way

Seven principles drive every decision below. When a design choice is ambiguous, return to these:

1. **The client can see what happened.** No mystery failures.
2. **The client can understand why, and how to resolve it** — via links to docs, support, and related resources.
3. **The client can communicate the issue to their user.** The response should help them do this.
4. **The client isn't forced into complex change management.** Breaking changes to error shapes are painful, so the design favours additive evolution.
5. **Resolution state is captured where it can be tracked.** Some issues are transient, some are ongoing.
6. **The shape is consistent across contexts** — responses, webhooks, callbacks, UI.
7. **It's clear where action is required** vs where the issue is advisory.

## Fields at a glance

| Field | Type | Required | Purpose |
|---|---|---|---|
| `issue` | namespaced string | Yes | The single machine-readable identity, `{domain}.{class}.{reason}` e.g. `payment.validation.missing_field` |
| `severity` | enum string | Yes | `error` (failed, action required), `warning` (succeeded, attention advised), `info` |
| `correlationId` | UUID string | Yes | Unique per request; the fastest way to find the issue in server logs |
| `dateTime` | ISO 8601 string | Yes | When the issue occurred, in UTC |
| `active` | boolean | No | Whether the issue is still ongoing; omit if you can't track it reliably |
| `message` | object | No | `{ title, detail }` human-readable copy, safe to surface to end users |
| `thirdParty` | object | No | `{ provider, code, message }` passed through verbatim from an upstream service |
| `links` | object | No | `{ documentation, portal, api }` to help the developer act |

Full field-by-field guidance — including the rationale, edge cases, and the third-party passthrough rules — is in [references/error-handling.md](references/error-handling.md). Read it before finalising a schema or reviewing one in depth.

## Design rules that are easy to get wrong

These are the choices that separate a usable error contract from a frustrating one:

- **Prefer descriptive string codes over numeric ones.** `payment.validation.missing_field` tells a developer what happened; `4012` makes them open a lookup table.
- **The `issue` code is the whole classification — `{domain}.{class}.{reason}`, read broadest to most specific.** `payment` is the resource/area, `validation` the kind of problem, `missing_field` the specific cause. There is deliberately **no separate `type` field**: it would only restate the `{class}` segment, and two fields that must always agree are a bug waiting to happen. Lead with the domain so codes stay unambiguous when issues from several resources flow through one channel (e.g. an aggregated webhook stream).
- **Parse by splitting on `.` and matching prefixes.** Branch on `payment.unauthorized`, treat any segment you don't recognise as "more specific than I handle," and never assume a fixed depth. Fall back to the `{class}` or `severity` you do know when a `{reason}` is unfamiliar.
- **Keep `issue` a plain string, not a strict enum — at least early on.** The taxonomy will grow; an exhaustive `switch` over an enum turns every new code into a breaking change for consumers. Commit to an enum only once the set has genuinely stopped moving.
- **Always generate a `correlationId`.** If the client sends `X-Correlation-ID`, echo it back so they can line up their logs with yours.
- **Omit `active` rather than lie.** A stale `active: true` is worse than no signal. Only include it when resolution state is genuinely tracked (e.g. a device offline until reconnect, an auth grant expired until re-auth).
- **`message` is a convenience, English-only.** Integrators may override the copy and own localisation. Don't block on perfect wording.
- **`thirdParty` is opaque.** Pass `provider`/`code`/`message` through unchanged, never build API logic on those values (use your own `issue` field), and assume it's *not* fit for end users.

## State and events: three carriers, three questions

A `status` field gets overloaded because it's quietly asked three different questions at once. Pull them apart and each gets a cleaner home:

- *What just happened?* → an **event**, a past-tense verb on the webhook envelope: `purchase.declined`.
- *Where is the resource now?* → the **status**, one persistent value driven by a state machine: `purchase.pending.payment_method`.
- *Why, and what should I do?* → an **issue**, the structured annotation above: `payment.declined.insufficient_funds`, with a severity, message, and links.

When a card is declined: the *event* is `purchase.declined`; the *status* reverts to `purchase.pending.payment_method` (the same value whether it's the first attempt or the fourth — failure loops back, it isn't terminal); and the *why* lives in an *issue*. The status stays honest about location; the issue carries cause and remedy.

Two namespaced strings — the status and the issue code — share one grammar, `{domain}.{primary}.{detail}`, read left to right and parsed by prefix. The middle segment differs by design: in a status it's the *state* (`pending`), in an issue it's the *class* of problem (`unauthorized`). The shape is shared so the parsing discipline can be too.

Full guidance — modelling the state machine, naming states vs events, the enum-vs-string trade-off, and the unresolved boundary around `active` — is in [references/event-status-design.md](references/event-status-design.md). Read it before designing a `status` field, naming webhook events, or building a lifecycle state machine.

## Consuming the pattern

The contract is only as good as how cleanly clients can consume it. For TypeScript types, a React form/handler example, and an SDK provider pattern, see [references/consuming-in-react.md](references/consuming-in-react.md). Point developers there when they ask how to *handle* these responses, not just shape them.

## Applying this skill

- **Designing a new endpoint's failures:** enumerate the ways it can fail, map each to a namespaced `{domain}.{class}.{reason}` `issue` code, and decide severity. Produce a concrete `issues` example, not just prose.
- **Designing a resource's lifecycle:** draw the state machine first (nodes are states, edges are transitions), name states for the obligation they imply (`requires_action` beats `pending`), keep failure recoverable where it can be, and split *what happened* / *where it is* / *why* across event, status, and issue. See [references/event-status-design.md](references/event-status-design.md).
- **Reviewing an existing API:** check it against the seven principles and the field table. The most common gaps are missing `correlationId`, numeric/opaque codes, errors and warnings split across different fields, no `links` to help the developer act, and a `status` field doing the job of an event or an issue.
- **Keeping it consistent:** the same `issues` shape should appear in responses, webhooks, and callbacks, and status/issue codes should share one grammar. Flag any context where the shape diverges.

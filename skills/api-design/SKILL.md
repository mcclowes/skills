---
name: api-design
description: 'Use when designing, reviewing, or implementing HTTP APIs — error and warning handling, resource state and lifecycle, read-endpoint structure, pagination, and authentication. Triggers on error responses and formats, response envelopes, webhook payloads, how an endpoint should fail; modelling a resource lifecycle (status fields, state machines, webhook event names, enum vs parseable string); structuring read endpoints (screen-shaped/BFF vs canonical resource, aggregation, cursor vs offset pagination); and auth design (security schemes, API keys vs bearer tokens, stepped-up tokens). Apply whenever an API surfaces a failure, state change, view of data, or auth requirement to a client.'
license: MIT
metadata:
  author: mcclowes
  version: "1.3.0"
---

# API design

Opinionated patterns for designing developer-friendly HTTP APIs. Several components are developed so far, and they're designed to fit together:

- **Error and warning handling** via a unified `issues` array — see below and [references/error-handling.md](references/error-handling.md).
- **State and events** — modelling a resource's lifecycle, and the split between *what happened* (event), *where the resource is* (status), and *why / what to do* (issue) — see [references/event-status-design.md](references/event-status-design.md).
- **View endpoints vs data endpoints** — whether an endpoint exists to render a screen or to expose a canonical entity, and why that changes shape, richness, and pagination. Includes pagination (cursor vs offset). See [references/view-vs-data-endpoints.md](references/view-vs-data-endpoints.md).
- **Auth schemes** — treating security schemes as discrete, named contracts rather than one undifferentiated "auth" blob. See [references/auth-schemes.md](references/auth-schemes.md).
- **Evolution and operations** — short stances on versioning and on not building infrastructure you can buy (see [Evolution and operations](#evolution-and-operations) below).

As more components are added (naming, data conventions), they live alongside these in `references/`.

## When this applies

Reach for this whenever an API needs to communicate that something went wrong, partially succeeded, or warrants attention — in a response body, a webhook, or a component callback. It also applies whenever you're modelling a resource's lifecycle (a `status` field, webhook events, a state machine), deciding whether a read endpoint should be screen-shaped or canonical, choosing a pagination style, or documenting how clients authenticate. The goal is responses a developer can act on without guesswork, and that they can relay to *their* end users.

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
- **Use US spelling for everything machine-readable.** Field names, enum values, `issue`/`status` codes, and webhook event names follow US spelling — `authorization`, `color`, `canceled`, `fulfillment` — never `authorisation`/`colour`/`cancelled`/`fulfilment`. It's the lingua franca of HTTP and existing standards (`Authorization` header, `Referer`), so it minimises surprise and keeps codes that flow through one channel internally consistent. This is a contract decision: spelling is part of the identifier, and changing it later is a breaking change. The one exception is human-readable `message` copy, which is English-prose and integrator-overridable (see the `message` rule above) — `"Payment not authorised"` is fine there.

## State and events: three carriers, three questions

A `status` field gets overloaded because it's quietly asked three different questions at once. Pull them apart and each gets a cleaner home:

- *What just happened?* → an **event**, a past-tense verb on the webhook envelope: `purchase.declined`.
- *Where is the resource now?* → the **status**, one persistent value driven by a state machine: `purchase.pending.payment_method`.
- *Why, and what should I do?* → an **issue**, the structured annotation above: `payment.declined.insufficient_funds`, with a severity, message, and links.

When a card is declined: the *event* is `purchase.declined`; the *status* reverts to `purchase.pending.payment_method` (the same value whether it's the first attempt or the fourth — failure loops back, it isn't terminal); and the *why* lives in an *issue*. The status stays honest about location; the issue carries cause and remedy.

Two namespaced strings — the status and the issue code — share one grammar, `{domain}.{primary}.{detail}`, read left to right and parsed by prefix. The middle segment differs by design: in a status it's the *state* (`pending`), in an issue it's the *class* of problem (`unauthorized`). The shape is shared so the parsing discipline can be too.

Full guidance — modelling the state machine, naming states vs events, the enum-vs-string trade-off, and the unresolved boundary around `active` — is in [references/event-status-design.md](references/event-status-design.md). Read it before designing a `status` field, naming webhook events, or building a lifecycle state machine.

## View endpoints vs data endpoints

The most consequential structural choice in an API is whether an endpoint exists to **render a view** or to **expose a resource** — they're different jobs, and the same data deserves a different contract depending on which. A view endpoint aggregates, derives, and formats data for one screen, owned by the frontend and changing fast; a data endpoint returns a normalised, raw, canonical entity, owned by the domain and changing slowly.

Build only one and the other job leaks somewhere worse: with only data endpoints the frontend stitches entities client-side (chatty, N+1, duplicated domain logic); with a "data" endpoint that tries to help, UI-specific fields accrete onto the canonical resource until you can't change a screen without a platform release. Naming the two jobs is what lets each stay honest.

**Pagination is the clearest case of this.** Cursor-based pagination is usually more efficient (cost doesn't grow as you page deeper, stable under inserts) and is fine for data endpoints and infinite scroll — but a UI that needs "page 3 of 47", jump-to-page, or total counts needs offset/page-number pagination, and that means accepting the database cost *because it's a presentation requirement*. The pagination style falls out of the job the endpoint does.

Full guidance — what changes between the two, the pagination trade-off, ownership, how they coexist, and the BFF/GraphQL/CQRS lineage — is in [references/view-vs-data-endpoints.md](references/view-vs-data-endpoints.md).

## Auth: discrete security schemes

Treat each way of authenticating as a **discrete, named scheme with its own contract**, and have every endpoint declare which *one* it requires — not "auth, somehow." The common failure is a jumbled mess where the consumer can't tell what to send to call a given endpoint.

Two traps, both seen in the wild:
- **Conflating the credential's mechanics with the scheme.** Codat left the relationship between "an API key" and `Authorization: Basic {base64 api key}` ambiguous — the key *is* the thing you base64-encode, but that mapping was never made explicit, so consumers couldn't turn what they had into what the API wanted. Describe the scheme from the consumer's side and state the transform.
- **Functionally distinct schemes sharing one implementation.** Weavr's stepped-up tokens are technically the same token as ordinary ones, but functionally they're different schemes: some endpoints require a stepped-up token, others accept a standard one, and an endpoint maps to one *or* the other. Scheme identity is the contract, not the mechanism.

Model it explicitly (OpenAPI's named `securitySchemes` + per-operation `security` already does exactly this). Full guidance and the worked examples are in [references/auth-schemes.md](references/auth-schemes.md).

## Evolution and operations

Two short, deliberately opinionated stances:

- **Co-version the ecosystem.** Keep the parts of an ecosystem versioned together for clarity — API version 6 goes with SDK version 6. This is hard to keep aligned and demands more considered change-management thinking, but the alternative (independently drifting versions a consumer has to reconcile) is worse. Beyond that, the skill stays thin on versioning on purpose.
- **Buy webhook infrastructure, don't build it.** Webhook *delivery* — retries, signing, dedup, ordering, replay, fan-out — is a solved, undifferentiated problem. Pay a service like [Svix](https://www.svix.com/) rather than reimplementing it. (Designing the webhook *payload* — the event and issue shapes — is still yours; see the state/events and error-handling components.)

## Consuming the pattern

The contract is only as good as how cleanly clients can consume it. For TypeScript types, a React form/handler example, and an SDK provider pattern, see [references/consuming-in-react.md](references/consuming-in-react.md). Point developers there when they ask how to *handle* these responses, not just shape them.

## Applying this skill

- **Designing a new endpoint's failures:** enumerate the ways it can fail, map each to a namespaced `{domain}.{class}.{reason}` `issue` code, and decide severity. Produce a concrete `issues` example, not just prose.
- **Designing a resource's lifecycle:** draw the state machine first (nodes are states, edges are transitions), name states for the obligation they imply (`requires_action` beats `pending`), keep failure recoverable where it can be, and split *what happened* / *where it is* / *why* across event, status, and issue. See [references/event-status-design.md](references/event-status-design.md).
- **Designing a read endpoint:** first decide whether it renders a view or exposes a resource, and shape it for that job — don't let one endpoint do both. Choose pagination to match (cursor for throughput, offset/page-number when a UI needs it). See [references/view-vs-data-endpoints.md](references/view-vs-data-endpoints.md).
- **Documenting auth:** enumerate the distinct schemes, name each, and make every endpoint declare the one it requires; keep the consumer-facing scheme separate from its implementation. See [references/auth-schemes.md](references/auth-schemes.md).
- **Reviewing an existing API:** check it against the seven principles and the field table. The most common gaps are missing `correlationId`, numeric/opaque codes, errors and warnings split across different fields, no `links` to help the developer act, a `status` field doing the job of an event or an issue, one endpoint trying to be both a view and a canonical resource, and an ambiguous/jumbled auth story.
- **Keeping it consistent:** the same `issues` shape should appear in responses, webhooks, and callbacks, and status/issue codes should share one grammar. Flag any context where the shape diverges.

# Error handling — full field reference

Detailed guidance for every field in the `issues` array. Read this when designing a schema from scratch, reviewing one in depth, or resolving an edge case the summary table in `SKILL.md` doesn't cover.

## Contents

- [The `issues` array](#the-issues-array)
- [`issue`](#issue)
- [`correlationId`](#correlationid)
- [`severity`](#severity)
- [`dateTime`](#datetime)
- [`active`](#active)
- [`message`](#message)
- [`thirdParty`](#thirdparty)
- [`links`](#links)
- [Open questions](#open-questions)

## The `issues` array

All non-success responses should include an `issues` array. It surfaces errors, warnings, and informational notices in one structure, giving developers enough context to understand what went wrong, whether it's resolved, and where to go next.

Errors and warnings share the same shape and the same need — context, traceability, a path forward — so splitting them into separate arrays would force developers to check two places for information that belongs to the same moment in a request's lifecycle.

## `issue`

**Type:** `string (namespaced)` — **Required:** Yes

The single machine-readable identity of the issue. Format: `{domain}.{class}.{reason}`, read left to right from broadest to most specific — e.g. `payment.unauthorized.token_expired`, `payment.validation.missing_field`.

- **`{domain}`** — the resource or area the issue belongs to (`payment`, `verification`, `account`). Leading with it keeps codes unambiguous when issues from several resources flow through one channel, such as an aggregated webhook stream, where `unauthorized.token_expired` on its own wouldn't say *what* was unauthorised.
- **`{class}`** — the kind of problem: `unauthorized`, `validation`, `conflict`, `rate_limit`, `internal`. The broad bucket most error handling branches on. Expand the set as the taxonomy matures.
- **`{reason}`** — the specific cause within that class: `token_expired`, `missing_field`, `invalid_format`.

This one code carries the whole classification — there is deliberately **no separate `type` field**. A standalone `type` would only restate the `{class}` segment, and two fields that must always agree are a bug waiting to happen. Consumers that need the class read it from the code instead (the second segment).

**Parsing, and strings vs enums.** Read the code by splitting on `.` and matching prefixes — branch on `payment.unauthorized`, treat any segment you don't recognise as "more specific than I handle," and never assume a fixed depth. Keep the values as plain strings rather than a strict enum at first: the taxonomy will grow, and an exhaustive `switch` over an enum turns every new code into a breaking change for your consumers. Fall back to the `{class}` you do know, or to `severity`, when a `{reason}` is unfamiliar. Commit to an enum only once the set has genuinely stopped moving.

Namespaced codes also let you express hierarchy without proliferating top-level values — `payment.validation.missing_field` and `payment.validation.invalid_format` are obviously related, where `missing_field` and `invalid_format` in isolation are just noise.

Prefer descriptive strings to numeric status and error codes. A developer reading `payment.validation.missing_field` understands it immediately; `4012` sends them to a lookup table.

## `correlationId`

**Type:** `string (UUID)` — **Required:** Yes

A unique identifier for the request. Use this when raising a support ticket or querying logs — it's the fastest way to locate the issue on the server side.

The API should generate a `correlationId` for every request. If the client supplies an `X-Correlation-ID` header, echo that value back, allowing them to correlate server logs with their own.

## `severity`

**Type:** `enum (string)` — **Required:** Yes

Whether the issue blocks the request or is advisory.

| Value | Description |
|---|---|
| `error` | Request failed; action required |
| `warning` | Request succeeded (or partially succeeded); attention advised |
| `info` | Informational notice only |

## `dateTime`

**Type:** `ISO 8601 string` — **Required:** Yes

When the issue occurred, in UTC.

## `active`

**Type:** `boolean` — **Required:** No

Whether the issue is still ongoing. Key where issues are persistent or stateful rather than transient. Useful for platform-level problems (e.g. a service degradation) where the issue may resolve without developer action.

A developer can disregard issues where `active === false`.

Real-world examples:
- A connected device goes offline — communicated as an active issue until the connection is re-established.
- A user's authorised access to a third-party data source expires or is revoked — an active issue until re-authorisation.

Omit this field if resolution state cannot be reliably tracked. A stale `active: true` is more harmful than no signal at all.

## `message`

**Type:** `object` — **Required:** No

A human-readable summary of the issue, suitable for surfacing to end users. Provided as a convenience — integrators may override this copy to match their own tone or context.

```json
{
  "message": {
    "title": "Payment not authorised",
    "detail": "This transaction couldn't be completed. Please check your card details or contact support."
  }
}
```

| Field | Description |
|---|---|
| `title` | Short, stable label. Suitable for a toast or modal heading. |
| `detail` | Fuller explanation. Suitable for inline help text or a support flow. |

Copy is not localised — provided in English only. Localisation is the integrator's responsibility.

## `thirdParty`

**Type:** `object` — **Required:** No

Present when the issue originates from a third-party service (e.g. a KYC or payment provider). Passed through as-is — the API does not transform or interpret this data.

```json
{
  "thirdParty": {
    "provider": "acme_verify",
    "code": "DOCUMENT_EXPIRED",
    "message": "The document provided has passed its expiry date."
  }
}
```

| Field | Description |
|---|---|
| `provider` | Identifier for the third-party service |
| `code` | The provider's own error code, if available |
| `message` | The provider's own error message, if available |

This data is unprocessed and may change if the underlying provider changes. Don't build logic that depends on specific `code` or `message` values — use the API's own `issue` field for that. This information is likely **not** suitable for end users.

## `links`

**Type:** `object` — **Required:** No

Relevant links to help the developer act on the issue.

| Field | Description |
|---|---|
| `documentation` | Docs page for this error type |
| `portal` | Support portal |
| `api` | Related API endpoint (e.g. retry, related resource) |

## Open questions

Unresolved design tensions worth flagging when they come up, rather than answering dogmatically:

- **Is the `issue` code stable enough to commit to as an enum?** Or is it better as a plain string to avoid breaking changes as the taxonomy evolves? (Current lean: plain string.)
- **Can you reliably track `active` / resolution state?** If not, defer it rather than implement it badly.
- **What should `links.api` point to?** A retry endpoint? A related resource? Needs clear, documented semantics per endpoint.
- **Should `issues` appear on 2xx responses too?** There's a case for surfacing `warning`/`info` alongside successful operations.

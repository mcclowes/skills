# Modelling the 3DS-pause state

Short version: don't add `requires_action`. It's the classic trap — it names the consumer's *to-do list* (go pop a challenge), not the *condition the charge is in*. Split that single signal into three carriers, each answering a different question:

- **Where is the charge right now?** → the **status**. Name it for the present condition: `authentication_required`.
- **What just happened?** → the **event** (on the webhook envelope): `charge.authentication_required` (past-tense transition).
- **Why, and what do I do about it?** → an **issue** carrying the 3DS challenge: the link to launch it, severity, and the copy you'd show the cardholder.

The frontend doesn't poll a status enum to decide whether to pop the challenge. It reads the **issue** — that's the layer built to carry "do this, here's the URL."

## Why not `requires_action`

`requires_action` is useful, which is exactly why Stripe shipped it and why it's tempting to copy. But notice what the word describes: the future tense in a status field. It tells the client to go *do* something rather than describing what the charge *is*. That's borrowing the status's job from a different carrier — the same instinct that produces `pending`, which is close to meaningless because every live state requires something next.

The actionability doesn't vanish when you drop the obligation from the name — it relocates. `requires_action` splits cleanly:

- a present-condition status, `authentication_required`, naming the missing piece (authentication is what's absent right now); and
- an issue that carries the *do this*: the challenge URL, the severity, the message.

The tell is word order. `authentication_required` reads as a condition (authentication is the gap). `requires_action` / `requires_authentication` reads as a demand to go act. **Lead with the missing thing.** The status stays a steady description of where things stand; the instruction lives in the layer designed for instructions.

## Fixing the enum: `failed` is the other problem

Your current enum is `pending | succeeded | failed`. Two issues, not one:

1. `pending` doesn't discriminate — it can't tell a 3DS pause apart from "we're authorising" or "we're capturing." It only separates done from not-done, which the terminal states already do.
2. `failed` treats failure as a terminal sibling of success. But **most payment failures aren't terminal** — a failed 3DS challenge, an abandoned challenge, or a decline should loop the charge *back* to a retryable state, not strand it in a dead end. Only genuine success and exhausted-retries / cancellation end the line.

Draw the machine before naming anything. Roughly:

```
[*] --> processing            (charge submitted)
processing --> authentication_required   (issuer requires 3DS)
authentication_required --> processing   (cardholder completed challenge)
authentication_required --> unpaid       (challenge failed / abandoned, retries remain)
authentication_required --> failed       (retry limit reached) [terminal]
processing --> succeeded                 (captured) [terminal]
processing --> unpaid                    (declined, recoverable)
unpaid --> processing                    (retried)
```

Every node is a present condition: the charge *is* processing, *is* authentication_required, *is* unpaid, *is* succeeded. None of them name what's owed or what just happened. Note `authentication_required` has multiple exit edges — back to `processing` on success, back to `unpaid` (or out to terminal `failed`) when the challenge fails — which a flat `requires_action` quietly hides.

## Recommended status values

Use a namespaced, dot-separated string rather than a bare enum, so the grammar matches your issue codes and consumers can parse by prefix and degrade gracefully:

```
charge.processing
charge.authentication_required
charge.unpaid
charge.succeeded
charge.failed         (terminal — retries exhausted / canceled)
```

Format is `{domain}.{state}`, broadest to most specific. `charge` is the domain (cheap to drop if your status field is always scoped to a charge, but keep it the moment statuses from several resource types flow through one webhook stream — `authentication_required` alone doesn't say *what* needs authenticating). If `processing` grows real substructure (authorising, then capturing), it can nest: `charge.processing.authorising`.

Keep it a forgiving string, not a strict enum, while the state set is still moving — an exhaustive `switch` over an enum turns every new status into a breaking change for your integrators. Document the parsing discipline: split on `.`, match on prefixes, treat unfamiliar deeper segments as "more specific than I handle," never assume a fixed depth. And answer the enum-vs-string question *once* — use the same call for both your status field and your issue codes; don't ship one strict and one forgiving.

## How the frontend learns to show the challenge

When the charge enters `charge.authentication_required`, return (and webhook out) an issue alongside it. The frontend's logic is "if there's an `authentication_required` issue, launch the challenge using `links.api`" — not "string-match the status."

```json
{
  "id": "ch_123",
  "status": "charge.authentication_required",
  "issues": [
    {
      "issue": "payment.authentication_required.three_d_secure",
      "severity": "error",
      "correlationId": "4b3a2c1d-0000-0000-0000-abcdef123456",
      "dateTime": "2026-06-04T12:34:56Z",
      "active": true,
      "message": {
        "title": "Verify your card",
        "detail": "Your bank needs to confirm it's you before this payment can go through."
      },
      "links": {
        "documentation": "https://docs.example.com/payments/3ds",
        "api": "https://api.example.com/charges/ch_123/authenticate"
      }
    }
  ]
}
```

Notes on the issue:

- **`issue` code** is `{domain}.{class}.{reason}` → `payment.authentication_required.three_d_secure`. The challenge URL / parameters the frontend needs to redirect or render the 3DS iframe live in `links.api` (or an additional structured field on the issue if you need more than a URL — e.g. a one-time challenge token, ACS URL, etc.). Don't smuggle that into the status.
- **`severity: error`** — the request can't complete until it's resolved, so action is required. (If you'd rather model the charge as "accepted, pending verification" you could argue `info`, but `error` is the honest read: nothing settles until the cardholder acts.)
- **`active: true`** is defensible *here* because this condition is genuinely ongoing and resolution-tracked — it flips to resolved once the challenge completes. This is one of the cases where an issue legitimately tracks a persistent state. Just make sure the issue's `active` and the `status` field never disagree about the same condition: the status is authoritative for "where is the charge," the issue is the notification plus the actionable link. If you can't reliably flip `active` to false, omit it rather than leave a stale `true`.
- **`correlationId`** on every issue; echo back an inbound `X-Correlation-ID` if the client sends one.

## When the challenge resolves

- **Completed successfully** → event `charge.authentication_completed`, status moves to `charge.processing` (then `charge.succeeded` on capture). The 3DS issue's `active` flips to false / it drops off.
- **Failed or abandoned** → event `charge.authentication_failed`, status returns to `charge.unpaid` (retryable) — *not* a terminal `failed`. The *why* rides in a new issue (`payment.declined.authentication_failed`, severity `error`), with a retry link while retries remain and none once they don't. The decline reason never enters the status; "show different copy on the second attempt" then falls out of the issue's message plus the presence of an earlier failure in history, with no bespoke `last_decline_reason` field.

## Keep one shape everywhere

The same `issues` array and the same `{domain}.{primary}.{detail}` grammar should appear in the charge response, the webhook payload, and any component callback. The frontend then handles 3DS, a plain decline, and a validation error with one code path — read the issues, branch on the prefix, follow `links.api`. That consistency is the whole payoff of not special-casing 3DS into a one-off status value.

## TL;DR

- Don't copy `requires_action`. It names the next step, not the present condition.
- Status → `charge.authentication_required` (a present-tense fact: authentication is the missing piece).
- Event → `charge.authentication_required` / `charge.authentication_completed` / `charge.authentication_failed` (past-tense transitions on the webhook).
- Issue → `payment.authentication_required.three_d_secure`, severity `error`, with the challenge URL in `links.api` — this is what the frontend reads to pop the challenge.
- Fix the enum while you're here: `pending` is non-discriminating and a terminal `failed` discards the retry path. Failure should loop back to `unpaid`; reserve terminal states for success and exhausted-retries/cancellation.
- Use a forgiving dot-string parsed by prefix, with the same grammar for status and issue codes, and US spelling for everything machine-readable (`authentication`, `canceled`).

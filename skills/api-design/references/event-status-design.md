# State and events — modelling and naming a resource's lifecycle

Guidance for designing a `status` field, naming webhook events, and modelling a state machine. Read this when an API needs to communicate *where a resource is* and *how it got there*, not just that something failed.

A `status` field is a contract, and it's where most APIs leak ambiguity — a single word doing the work of three, consumed by people who weren't in the room when you named it. Get it right and an integrator builds correct handling from the payload alone. Get it wrong and they reverse-engineer your intentions from support tickets.

## Contents

- [Status, event, issue: three questions](#status-event-issue-three-questions)
- [The naming trap: don't name a state for what's needed next](#the-naming-trap-dont-name-a-state-for-whats-needed-next)
- [Failure is usually not terminal](#failure-is-usually-not-terminal)
- [Start with the diagram](#start-with-the-diagram)
- [Four questions to place a state](#four-questions-to-place-a-state)
- [Three things every status should carry](#three-things-every-status-should-carry)
- [The middle segment is an axis, not a fixed slot](#the-middle-segment-is-an-axis-not-a-fixed-slot)
- [Naming: events vs states](#naming-events-vs-states)
- [Enums or parseable strings](#enums-or-parseable-strings)
- [A parent segment is a container or a value, never both](#a-parent-segment-is-a-container-or-a-value-never-both)
- [The shared grammar with issue codes](#the-shared-grammar-with-issue-codes)
- [The unresolved boundary: `active`](#the-unresolved-boundary-active)
- [The shape of a good rule](#the-shape-of-a-good-rule)

## Status, event, issue: three questions

A status field gets overloaded because it's asked three questions at once, and they aren't the same question. Pull them apart and each gets a cleaner home:

- *What just happened?* → the **event** — a past-tense verb on the webhook envelope. `purchase.declined`.
- *Where is the resource now?* → the **status** — one persistent value, the state machine. `purchase.unpaid`.
- *Why, and what should I do about it?* → an **issue** — a structured annotation carried alongside the response, with a namespaced code, a severity, a human-readable message, and links to docs, retry, or support. See [error-handling.md](error-handling.md).

The status is the one that gets overloaded, because it's the one with a job that's easy to hand to a neighbour. Name a state for what just *happened* and the status becomes the last event echoed back. Name it for what must happen *next* and it becomes a to-do list. Either way it's borrowed its job from a carrier that already does it — the event carries the past, the issue carries what to do. The one job left over, the status's own, is the present tense: what the resource *is* right now.

The failure case shows why the separation pays. When a card is declined: the event is `purchase.declined`; the status reverts to `purchase.unpaid` — the purchase's present condition, the same value whether it's the first attempt or the fourth; and the reason lives in an issue, `payment.declined.insufficient_funds`, severity `error`, with a retry link while retries remain and none once they don't. The decline reason never enters the status.

A useful consequence: a "show different copy on the second attempt" requirement falls out for free — it's the issue's message, plus the presence of an earlier decline in the history. You don't need an `unpaid.awaiting_new_card` state, which would only name an obligation and then beg the question of what the third attempt is called. And the *why* never wants a bespoke `last_decline_reason` field; it's the same consistent `issues` structure used everywhere else — one pattern, every surface.

## The naming trap: don't name a state for what's needed next

There's a tempting pattern, and it's a trap. Stripe's `PaymentIntent` names states by what's needed next — `requires_payment_method`, `requires_confirmation`, `requires_action`. `requires_action` tells the consumer to *do something*: surface a 3DS challenge. That's useful, which is why the pattern spreads. But notice what the name describes — the consumer's to-do list, not the resource's condition. It's the future tense in a status field.

The same instinct produces `pending`, and `pending` is the tell. It's close to meaningless: every live state is pending something, every live state requires something next, so the word only separates "not done" from "done" — which the terminal states already tell you. It's the one name guaranteed not to say which state you're actually in. `requires_` is the same word with the obligation spelled out; it discriminates a little better, but it's still describing the future instead of the present.

**Drop the obligation from the name and the actionability doesn't vanish, it relocates.** `requires_action` splits into a present-condition status — `authentication_required`, naming the missing piece — and an issue that carries the *do this*: the challenge link, the severity, the copy you'd show a user. The status stays a steady description of where things stand; the instruction lives in the layer built for instructions.

## Failure is usually not terminal

A declined card doesn't move to a dead-end `failed` state; the resource returns to `unpaid` so the payment can be retried. Only success and explicit cancellation end the line.

`failed | succeeded` treats failure as a sibling of success — an exit. But most failures are recoverable, and a terminal `failed` discards the path back. Ask of every failure: *is this the end, or a detour?* Usually it's a detour. Reserve genuinely terminal states for the small set of conditions that truly can't continue (retry limit reached, explicit cancellation).

## Start with the diagram

Before naming anything, draw the machine. Nodes are states, edges are transitions; transitions may be conditional, bidirectional, or guarded. Drawing it does two things:

- It shows where you've **over-specified** — states that can be collapsed because nothing distinguishes their transitions.
- It shows where you've **under-specified** — a single state whose edges are doing visibly different jobs, asking to be split.

```mermaid
stateDiagram-v2
    [*] --> draft: checkout opened
    draft --> void: abandoned

    state processing {
        [*] --> authorising
        authorising --> clearing: authorised
    }

    draft --> processing: submitted
    unpaid --> processing: submitted
    processing --> paid: captured
    processing --> unpaid: declined / recoverable
    processing --> void: declined / retry limit reached

    paid --> [*]
    void --> [*]
```

Every name in that picture is a present condition: the purchase *is* a draft, *is* unpaid, *is* processing, *is* paid, *is* void. None of them say what's owed or what just happened. Note too what the diagram forces into the open. A decline has *two* edges, not one — back to `unpaid` when the buyer can try again, out to `void` only when retries are exhausted. `processing` has internal structure (authorising, then clearing) because those substates have genuinely different transitions. If they didn't, they'd be one state.

## Four questions to place a state

The diagram gives you the nodes. The next step is working out what *kind* of state each one is, because the kind decides the name. Four questions do most of the work, and each feeds a naming choice.

- **Is the system working, or waiting?** Either the system is doing something it will finish on its own, or the resource is parked waiting on someone else to act. The two clear differently and they name differently (see [Naming](#naming-events-vs-states) below).
- **Is it terminal?** Does the line end here, or does the resource move on? Keep terminal states for genuine ends — success, rejection, cancellation — and remember failure usually isn't one; it loops back.
- **Who unblocks it?** The system, the customer, a third party, or you. Even when this doesn't drive the status name, it decides the next move: a state someone else owns is one you wait or chase on, not one you act on. It can also become the axis you group by (see below).
- **Does it turn on a clock?** A state that can expire — an SLA, a settlement window, an authentication that lapses — needs an explicit transition for the timeout, and usually an issue carrying the deadline while the clock runs.

None of these is a naming rule by itself. They're the questions the name should answer, so a consumer reading the status reconstructs them without asking you.

## Three things every status should carry

A well-formed status is three segments in one string — `{domain}.{state}.{substate}` — so `purchase.processing.authorising` reads as a purchase (domain) that is processing (state), specifically authorising the payment (substate). Each segment is broader than the one after it.

- **Domain.** The resource or area the status belongs to. In a single endpoint it's usually implied — but it stops being implied the moment an aggregated webhook consumer fields events from several resource types. Encode it so the status is legible without its envelope. *A status that only makes sense once you know which endpoint delivered it is half a status.*
- **State.** The condition the resource is in: `draft`, `unpaid`, `processing`, `paid`, `void`. Each names what the resource *is*. This is the part most people mean by "status."
- **Substate.** Genuine substructure within a state. `processing` almost always has it — authorising, clearing, settling — and those may nest further, because each substate has different transitions. **Be careful what you let in here:** the substate is for *where* the resource is, not *why* it got there. A substate that starts absorbing failure reasons is quietly turning into an error field — that belongs in an issue.

## The middle segment is an axis, not a fixed slot

The section above calls the middle segment "the state," and in the purchase example it is one. But that's the default, not a law. The middle segment is really an *axis* — the dimension you've chosen to group by — and the state is just the most common choice. Two others earn their keep:

- **Phase** — the stage of the lifecycle the resource sits in. A KYB onboarding running `kyb.disclosure.not_started`, `kyb.disclosure.incomplete`, `kyb.disclosure.complete`, where `disclosure` is the phase and the leaf says where the subject is within it.
- **Sub-process** — as the purchase's `processing` does, gathering the in-flight states (`authorising`, `clearing`) under one composite.
- **Actor** — who owns the next move (the third of the four questions above). `kyb.awaiting_user.not_started` collects every state where the ball is in the subject's court, against a `kyb.in_review` where it's in yours.

The choice matters because the prefix is the cheap thing to branch on. A consumer splits on the dot and matches the middle segment without reading further, so whatever sits there is the question you've made easiest to answer. Group by actor and "whose move is it" is a one-segment match; group by phase and "what stage are we at" is. You can usually recover the other axes — phase carries the actor almost for free — but recovery costs a lookup the prefix would have saved.

So pick the axis your dominant consumer reads most. A dashboard chasing the right party wants the actor up front; a pipeline view tracking progress wants the phase. The grammar doesn't change. What changes is the question you've answered for free.

## Naming: events vs states

Start with the edges, because verbs are easier to agree on than nouns.

- **Events are past-tense verbs**, namespaced to the domain: `purchase.submitted`, `purchase.authorised`, `purchase.captured`, `purchase.declined`. They record a transition that has completed — the past tense is the point.
- **States are conditions, and a condition is true in the present.** Don't conjugate everything to `-ed` to match the events (`drafted`, `pendinged` is nonsense), and don't reach for `requires_` or `pending` to say what's owed — neither names the present. The rule that matters isn't a suffix; it's three things at once: each name describes a present condition, the category stays consistent (pick adjectives, or pick participles, and stay there), and the states stay distinct from the events.

**Naming the present condition has two shapes, and which one fits turns on who resolves the state** — the first of the four questions.

- **When the *system* is doing the work** — authorising a charge, clearing funds, running a check — something genuinely is in progress, and the present-progressive `-ing` is exactly right: `authorising`, `clearing`. The name says what the machine is busy with, and the state clears itself with no one prompted.
- **When the resource is parked waiting on someone else** — usually the user — nothing is in progress and an `-ing` would lie. Name what's *blocking* it: `unpaid`, or `authentication_required` for the 3DS state. That's still a present fact (what's missing right now), and unlike `pending` it discriminates — it says *which* gap you're stuck on, which is what the consumer has to act on.

The tell is word order: `authentication_required` reads as a condition (authentication is the missing piece), while `requires_authentication` reads as a demand to go and do something. The first describes the present, the second points at a future step. **Lead with the missing thing.**

The distinctness from events is more than cosmetic. When the natural name for a state is the same word as the event that produced it — the `captured` event lands you in a `captured` state — that collision is a **diagnostic**, not a coincidence. It usually means the state is just "the last event, echoed back": you've recorded *what happened* in the field that's supposed to tell you *where you are*. A well-formed state names the condition the entity is now in, generally a different word from the transition that got it there. If you can't find that different word, the model is probably under-specified.

The disambiguation that always works is structural, not lexical: events and states live in different fields and different namespaces. `event.type` is one thing; `object.status` is another. Even when the vocabulary overlaps, the location resolves it.

## Enums or parseable strings

Decide whether your state space is stable enough to commit to an enum. If you expect to add or split statuses, every addition is a potential breaking change for anyone who wrote an exhaustive `switch` — a real cost, paid by your integrators, not you.

The dot-separated string is the usual middle path:

```json
{ "status": "purchase.processing.authorising" }
```

The whole string carries a specific meaning, and the consumer can `split('.')` it to act on the parts — branch on the domain, group by the middle segment, drill into the substate. It degrades gracefully: code that only cares about `purchase.processing` matches the prefix and ignores what follows.

But be honest about the trade: you haven't removed the breaking-change problem, you've moved it somewhere less visible. The moment consumers parse the string, its *grammar* is the contract — the segment count, the ordering, the meaning of each position. Add a fourth segment and you break exact-match consumers while sparing prefix-match ones. So **document the discipline**: match on prefixes, treat unknown deeper segments as "more specific than I handle," never assume a fixed depth. An implicit grammar nobody documented is more fragile than an enum, precisely because nobody agreed to it.

Reason-as-field versus reason-as-segment is a genuine fork (Stripe keeps the *why* in a sibling `cancellation_reason: fraudulent`). A segment keeps everything legible in one string and survives transport that drops sibling fields; a field is easier to extend and make optional without touching the status contract. Either way, the *why* belongs beside the status, not inside it — and the consistent place for it is an issue.

## A parent segment is a container or a value, never both

Grouping by a middle segment forces one more decision: whether that segment is ever a state in its own right. It can't be both, and the failure is quiet.

Say a review has an in-progress condition and two outcomes. The compact temptation is to let a bare `kyb.review` mean "in review," with `kyb.review.approved` and `kyb.review.rejected` for the outcomes. It reads well. But now a consumer matching the prefix `kyb.review` can't separate "still in review" from "review concluded, approved" — the bare value and its own children fall under the same match. The prefix has stopped discriminating the one thing the consumer most needs to know.

So keep parents honest: a segment is either a **pure container**, where every state under it carries a leaf (`review.in_progress`, `review.approved`, `review.rejected`, no bare `review`), or it's a **flat state with no children**. A bare parent that also has children is exactly the case where `startsWith` lies — and prefixes not lying was the whole reason to prefer a dot-string over an opaque code.

The trap is worst with terminal children. Were the children all sub-conditions of being in review (`review.escalated`, `review.awaiting_committee`), a bare parent would at least be honest, since they're all kinds of "in review." It's the children that mean review is *over* that turn the bare parent into a false signal.

## The shared grammar with issue codes

The status and the issue code share one grammar: `{domain}.{primary}.{detail}`, read left to right from broadest to most specific, parsed by prefix. The domain plays the same role in each. The middle segment does **not**, and that difference is the convention, not an inconsistency:

| | middle segment | answers |
|---|---|---|
| **status** | the *state* (`unpaid`) | *where is the resource?* |
| **issue** | the *class* of problem (`unauthorized`) | *why did something go wrong?* |

The shape is shared so the parsing discipline can be too. Both therefore face the same enum-or-string question — answer it **once**. Shipping the issue code as a forgiving string and the status as a strict enum (or the reverse) is a seam with nothing behind it.

## The unresolved boundary: `active`

One field resists the tidy split: an issue's `active` flag — is this still ongoing, or already resolved? For a decline it's clean (it happened, it's over, the status holds whatever condition persists). But the moment an issue is `active`, persistent, and resolution-tracked — a device offline until it reconnects, an authorisation revoked until re-granted — the issue has started asserting a *state*. That's a second state machine hiding in a boolean, free to disagree with the status field that should own the same condition.

The line worth holding: **status is the resource's current condition** — one value, persistent, authoritative. **Issues are annotations on a response** — many, mostly transient, carrying cause and severity and remedy. When an issue wants to be persistently `active`, treat that as a signal the condition deserves a status of its own, and let the issue shrink back to *the notification that the status changed*.

Where exactly that border falls — and whether `active` means "this request was blocked" or "this condition is ongoing," because it can't cleanly mean both — is genuinely open. Flag it rather than answering dogmatically. (See also the `active` field in [error-handling.md](error-handling.md).)

## The shape of a good rule

Name the transition for what happened. Name the state for what *is* — the present condition, not the last event and not the next obligation. Keep the vocabularies apart, and treat the cases where you can't as a question about your model rather than a quirk of English. Carry the domain even when it feels implied, because one day it won't be. And before you commit a status to the wire, ask what it's there to answer: *given this, what is true of the resource right now?* If the name answers that cleanly, it's done its job. The other question the consumer has — *so what do I do?* — isn't the status's to answer alone, and that's no failing: part of that answer belongs to the event that got them here, part to the issue that says what's wrong. Three carriers, three questions — the discipline is keeping each to its own.

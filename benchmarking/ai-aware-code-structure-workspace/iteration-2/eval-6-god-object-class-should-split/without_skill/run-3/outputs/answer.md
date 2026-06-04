# Split it

Short version: no, keeping it together isn't the right call. I'd split `UserService` into focused modules. Your instinct about Claude having "everything in one place" is reasonable but it's solving the wrong problem, and the cost outweighs the benefit.

## Why the "one place" reasoning doesn't hold up

The intuition is that a single file means no hunting. But that's true for a human scrolling, not for how an AI agent actually works on a codebase. A few things break down:

- **Claude doesn't read files the way you scroll them.** It searches, greps, and reads targeted ranges. When it needs to fix a token-validation bug, having 420 lines of email and analytics code in the same file isn't "convenient context" — it's noise it has to load, parse, and hold in its working context. It increases the surface for the model to accidentally touch unrelated code (e.g. "while I'm here, let me tweak the email retry" on a profile-update task).

- **A 420-line file with four unrelated responsibilities is harder to reason about than four 80–120 line files with one each.** The whole point of a clear module boundary is that the agent (and you) can load *just* the auth concern and be confident nothing about analytics is going to bite. Co-location of unrelated concerns destroys that guarantee.

- **Blast radius.** When everything shares a class, edits to one concern ripple. Shared private state, shared imports, shared constructor wiring. An agent editing the email logic now has to understand the auth fields on `this` to avoid breaking them. Smaller, single-purpose units mean a smaller, more predictable blast radius for any change — which is exactly what you want when an LLM is making the change semi-autonomously.

## The actual smell

This is a textbook god object. The four things you listed are genuinely different concerns with different reasons to change, different dependencies, and different testability profiles:

1. **Auth / tokens** — issuing and validating. Depends on a signing secret / JWT lib. Pure-ish, very unit-testable.
2. **Profile CRUD** — talks to the database. Depends on your DB client / ORM.
3. **Transactional email** — talks to an email provider. Side-effecting, wants to be mockable.
4. **Analytics events** — fire-and-forget telemetry. Should never block or break the core flow.

The tell is that #3 and #4 are *side effects that hang off* the real operations, not part of them. "Send a welcome email" and "fire a `user.created` event" are reactions to "create a profile," not the same responsibility.

## What I'd do instead

Split along those seams:

```
auth/
  tokenService.ts        // issue, verify, refresh
profile/
  profileRepository.ts   // DB CRUD only
notifications/
  userEmailer.ts         // transactional email
analytics/
  userEvents.ts          // analytics event firing
```

Each gets its own focused unit and its own test file alongside it.

Then decide how the side effects get triggered. Two reasonable options:

- **Thin orchestrator.** Keep a slim `UserService` (or use-case functions like `registerUser`) that depends on the four modules and composes them: write profile, then send email, then fire event. It owns the *sequence*; the modules own the *work*. This keeps call sites simple while the heavy logic stays separated and independently testable.
- **Event-driven.** Profile CRUD emits a domain event (`UserCreated`) and the emailer and analytics subscribe. More decoupled, better if email/analytics shouldn't be able to fail the write. More machinery than a ~420-line service probably warrants today, so I'd reach for this only if you already have an event bus or you specifically want that isolation.

For most apps at this size, the thin orchestrator is the right amount of structure. Don't over-engineer it into a full event system unless you have a concrete reason.

## Bonus wins from splitting

- **Testing gets dramatically easier.** Right now, to test token validation you have to construct a `UserService` that also wants a DB connection and an email client. Separated, each unit takes only the dependencies it actually uses. That's better for you and better for Claude writing tests.
- **Failure isolation.** Analytics should never break a signup. With it tangled into the service, it's easy to forget to wrap it. As its own module with a clear boundary, "this is best-effort, swallow errors" lives in one obvious place.
- **Clearer dependency graph.** Auth no longer transitively drags in your email SDK.

## One caveat

Don't shatter it into a dozen tiny files either. Four-ish cohesive modules plus a thin composition layer is the target. The goal isn't "smaller files," it's "one reason to change per file." A module that's 120 lines but does exactly one thing is better than both your current 420-line god object *and* a pile of 15-line fragments that force the agent to hop across ten files to follow one flow.

So: split by responsibility, keep a thin orchestrator to preserve simple call sites, test each piece in isolation. Claude will navigate that *better* than the monolith, not worse.

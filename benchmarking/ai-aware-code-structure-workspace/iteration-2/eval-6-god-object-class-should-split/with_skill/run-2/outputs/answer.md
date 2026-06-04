Short answer: no, I'd split this — but not because of a line-count reflex, and not into the four files you might expect. The "keep it together so Claude never has to hunt" instinct is right about the failure mode (agents really are reluctant to look at adjacent files), but wrong about the cure here.

## Why the instinct backfires in this specific case

Co-location wins when the pieces are *tightly coupled* — when you can't understand one without the other, so keeping them together means the agent works from a complete picture instead of a partial one. That's the case where merging genuinely beats splitting.

Your UserService isn't that. Auth-token issuing/validation, profile CRUD, transactional email, and analytics events are four concerns that don't need each other to be understood. The test I'd apply is: **can each concern be understood in isolation?**

- Token logic: understandable on its own (secrets, signing, expiry, verification).
- Profile CRUD: understandable on its own (DB reads/writes against the user table).
- Transactional email: understandable on its own (template + send).
- Analytics: understandable on its own (fire event with payload).

All four pass the isolation test. That's the signal that the boundary between them is real, not artificial. When you split here, each resulting file stands alone — the agent can edit the email logic without ever needing to open the token code. So you're *not* paying the cross-file-context tax that makes splitting dangerous. The "doubled lookups the agent won't perform" cost simply doesn't apply, because there's nothing to look up across the boundary.

Meanwhile the 420-line god object is actively hurting you in the way that matters for an agent. When you ask Claude to touch the email flow, it loads all 420 lines — token signing, DB queries, analytics — as noise. High signal-to-noise produces better output; this is the opposite. A focused ~80-line email module is a far better prompt than a 420-line file where 80% is irrelevant to the task.

So this is the case where the human reader, the maintainer, and the agent all want the same thing. There's no real tension to resolve.

## What I'd actually do

Split by concern into focused, self-contained modules:

- `auth-tokens.ts` — issue + validate
- `user-repository.ts` — profile CRUD against the DB
- `user-emails.ts` — transactional email
- `user-analytics.ts` — event firing

Keep `UserService` as a thin orchestrator that composes them (e.g. `signup()` calls the repo, then the email module, then analytics). That orchestrator stays small and readable, and each dependency is a *real abstraction* — Claude reads `emails.sendWelcome(user)` at the call site and knows enough to proceed without opening the email file. That's the key point: an abstraction reduces the context needed, whereas splitting alone just relocates code. You're getting the abstraction, which is the higher-value move.

This also buys you the things you'd want anyway: you can unit-test token validation without standing up a DB, mock email in profile tests, and swap the analytics sink without touching auth.

## Where I'd push back on going further

Don't over-fragment. Resist splitting any single one of these into "logic + thin wrapper" pairs (e.g. an email "service" plus an email "sender" that only make sense read together). Each concern should be **one cohesive file**, even if it runs 150–200 lines. A coherent 180-line module beats two 90-line files that are meaningless apart. The ~300-line ceiling is where signal-to-noise forces a split; below that, cohesion wins. The problem with your current file isn't its size, it's that it's four unrelated things — fix the right thing.

## Rule of thumb to carry forward

Co-locate when pieces need each other for context; split when each piece stands alone. "Keep it together so the agent doesn't hunt" is correct for tightly-coupled logic+rendering, but it's the wrong reflex for a service bundling independent concerns — there's nothing to hunt for, and the bundle just dilutes every prompt.

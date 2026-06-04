# Split it — but not because it's "too big"

Your instinct ("keep it together so Claude has everything in one place") is the right instinct applied to the wrong boundary. Co-location wins when the pieces actually need each other to make sense. Yours don't.

## The test that matters

The useful question isn't "is this a separate concern?" — it's **"can each concern be understood in isolation?"** Run it across your four responsibilities:

- **Auth tokens** (issue/validate) — understandable alone. Inputs are credentials/claims, outputs are tokens or a boolean. No knowledge of email templates or analytics needed.
- **Profile CRUD** — understandable alone. It's database reads/writes against a user record.
- **Transactional email** — understandable alone. Takes a recipient and some data, sends.
- **Analytics events** — understandable alone. Fire-and-forget, depends on nothing else here.

All four pass the isolation test independently. That's the tell: this isn't tightly coupled logic that splitting would shred into mutually-meaningless halves. It's four loosely-related capabilities that happen to share a class name. The thing keeping them together is the file, not the code.

## Why "one place" backfires here

The "never has to go hunting" theory assumes the agent benefits from having all 420 lines in context. In practice it cuts the other way:

- **Signal-to-noise.** When you ask Claude to tweak token expiry, the email templating and analytics payloads are pure noise in the window — they cost tokens and dilute attention without informing the change. A focused ~100-line auth module is a far better prompt than a 420-line grab-bag.
- **Past the ceiling.** Cohesive files can comfortably run to a few hundred lines, but that allowance is for *one coherent concern*. 420 lines across four unrelated concerns is exactly the case where signal-to-noise becomes the problem. You're over the line for the wrong reason — multiple concerns, not size alone.
- **No cross-file penalty to avoid.** The real cost of splitting is the cross-file lookup an agent won't perform — props shaped in a sibling, types defined elsewhere. That penalty doesn't apply here because the four pieces don't reference each other's internals. Splitting them creates no dangling context. (Contrast: splitting a "smart" component's logic from its rendering, where each half is meaningless without the other — *that's* the split you'd avoid.)

So you get the focus benefit with none of the usual splitting cost. That's the ideal case for separating.

## What I'd actually do

Split by capability, each file self-contained:

- `auth/tokens.ts` — issue + validate (keep these together; they're a genuine pair, share signing keys/claim shapes, and are always reasoned about as a unit)
- `users/profile.ts` — profile CRUD against the DB
- `notifications/email.ts` — transactional email
- `analytics/events.ts` — event firing

Then the question is what's left of `UserService`. Two good options:

1. **Delete it.** If it was just a namespace, let callers import the capability they need. A route handler doing profile updates imports `users/profile.ts` and nothing else — minimal, accurate context.
2. **Keep a thin orchestrator** *only* if you have real workflows that compose these — e.g. "sign up" = create profile, then send welcome email, then fire `user.signed_up`. That orchestration is its own coherent concern and earns its own small file. It reads as four well-named calls; the agent understands it from the call sites without opening the implementations.

Option 2 is the better framing of your original goal. You wanted a single entry point so nothing gets missed — but the right tool for that is **a named abstraction, not a god file**. `registerUser()` calling `createProfile()`, `sendWelcomeEmail()`, `trackSignup()` gives an agent the whole flow at a glance *and* keeps each implementation isolated and editable. An abstraction reduces the context needed to work with the code; a 420-line file just relocates all of it into one window.

## One thing to watch

Make sure the split lines up with the seams, not against them. If token validation currently reaches directly into the profile DB query (say, to load a user during validation), don't sever that into two files that each only half-make-sense — give the auth module a clean function it calls (`getUserById`) so each side still stands alone. The boundary is right when you can open any one file and edit it without needing the others. If a split would leave a file referencing values only explicable by reading a sibling, the cut is in the wrong spot — move it or keep those two pieces together.

## Bottom line

Split it. Four capabilities that each pass the isolation test belong in four files; the togetherness you wanted is better served by a thin orchestrator or by direct imports. You'll give Claude *more* relevant context per task, not less — the win of co-location only shows up when the pieces genuinely need each other, and yours don't.

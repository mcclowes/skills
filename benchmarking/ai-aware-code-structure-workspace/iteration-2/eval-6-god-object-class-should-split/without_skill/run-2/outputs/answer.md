# Split it. The "one place" intuition is backwards here.

Short version: no, I'd split it. Your reasoning is intuitive but it optimizes for the wrong thing. Let me make the case.

## Why "keep it together" doesn't actually help Claude

The premise is that a single file means an agent "has everything in one place and never has to go hunting." But that's not how an LLM (or a human) pays the cost of a large file:

1. **You pay the whole file on every edit.** When Claude touches the email-sending logic, it reads (and reasons over) the 420 lines of auth, profile CRUD, and analytics it doesn't need. That's context budget spent on noise, and noise measurably degrades edit accuracy. A focused 80-line file is *cheaper* and *safer* to edit than one quarter of a 420-line file.

2. **"Hunting" is cheap; reasoning is expensive.** Finding the right file via a grep or a clear name costs almost nothing. The expensive failure mode is an agent editing the wrong thing, or breaking an unrelated concern because it was sitting in the same blast radius. A god object maximizes blast radius — a change to token validation sits three feet from a change to your analytics payload, and the model has to hold both in its head to be sure it didn't break one while editing the other.

3. **Unrelated concerns create false coupling in the model's mental model.** Because everything is one class, Claude will tend to reach for `this.db`, `this.emailClient`, `this.analytics` from anywhere, because they're all in scope. That makes the *next* change harder to reason about, for both you and the agent. Separation isn't bureaucracy — it's what lets an agent confidently say "this change can only affect tokens."

## What you actually have: four concerns, not one

`UserService` is doing four genuinely unrelated jobs:

- **Auth** — issuing and validating tokens (crypto/JWT, secrets, expiry)
- **Profile** — CRUD against the database (persistence, validation)
- **Email** — transactional sends (a network side effect, an external provider)
- **Analytics** — firing events (another network side effect, fire-and-forget)

These don't share state or invariants. They share the *word* "user," which is not the same thing. That's the classic signature of a god object: cohesion by topic, not by behavior.

The tell: **they fail and change for different reasons.** Your email provider rotates an API key; your token format gets a new claim; your analytics vendor changes its event schema; your DB schema migrates. Four independent reasons to change one file means four independent ways to break the other three.

## Concrete recommendation

Split along the four seams, and let dependencies flow one direction:

```
src/user/
  auth/tokenService.ts        // issue(), validate() — knows about secrets + expiry, nothing else
  profile/profileRepository.ts // CRUD, the only thing that touches the DB for users
  profile/profileService.ts    // profile use-cases, orchestrates the repo
  notifications/userEmailer.ts // transactional sends, wraps the email provider
  analytics/userEvents.ts      // event firing, wraps the analytics client
  index.ts                     // optional barrel for the public surface
```

Then decide where orchestration lives. "Sign up a user" might: create a profile, send a welcome email, fire a `user_signed_up` event. That cross-concern flow belongs in a thin **use-case / handler** that *calls* the four pieces — it doesn't belong *inside* any of them:

```ts
// profile/registerUser.ts
export async function registerUser(input: RegisterInput, deps: {
  profiles: ProfileRepository;
  email: UserEmailer;
  events: UserEvents;
}) {
  const profile = await deps.profiles.create(input);
  await deps.email.sendWelcome(profile);   // consider awaiting vs fire-and-forget
  deps.events.track("user_signed_up", { userId: profile.id });
  return profile;
}
```

Passing dependencies in (rather than `new`-ing them inside) is what makes each piece independently testable — you can unit-test token validation without a database, and test registration with fakes for email and analytics. That maps directly onto the TDD workflow you favor.

## Guardrails so the split doesn't get worse than the god object

- **Don't over-fragment.** Four-to-six files here, not twenty. A file per *method* is the opposite failure and is just as hard to navigate. The unit is the concern, not the function.
- **Keep types close to their owner.** `TokenPayload` lives with the token service, not in a shared `types.ts` dumping ground.
- **One direction of dependency.** Auth and the repository shouldn't import the emailer or analytics. Orchestration sits on top and depends on all of them. No cycles.
- **Co-locate tests** — `tokenService.test.ts` next to `tokenService.ts`, etc.

## When the monolith would've been fine

If this were genuinely *one* cohesive concern split across artificial files, I'd tell you to merge it — small, tightly-coupled things that always change together belong together, and over-splitting hurts agents too. The rule isn't "small files good." It's **one reason to change per file.** Your `UserService` has four. That's the line it crosses.

## Bottom line

Splitting here makes Claude's job easier, not harder: smaller context per edit, smaller blast radius, clearer "this change can only affect X" reasoning, and tests that don't need the whole world stood up. The "everything in one place" instinct is the right instinct applied to the wrong boundary — keep things together when they change together, and these four don't.

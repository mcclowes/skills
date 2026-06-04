# Move most types next to the code that owns them

Short answer: a single central `types.ts` is the thing I'd move away from, especially since you're editing mostly through Claude Code. "Single source of truth" is a good instinct, but it means each type is *defined once* — not that every definition lives in *one file*. You can keep the former while dropping the latter.

## Why the central file hurts more in an AI workflow

The cost isn't really the 400 lines. It's that `types.ts` is the sibling file an agent won't open. AI tools are strikingly reluctant to go look at adjacent files — they work confidently from whatever's in the current buffer. So when Claude is editing a service and the type it needs is defined in `types.ts`, one of two things happens:

- It chases the import into the central file (a hop on the exact axis agents are weakest), or
- More often, it guesses the shape from usage and edits confidently wrong.

And the failure mode compounds: when you change a type *and* the code that uses it, those are now two edits in two files. The agent reliably does the first and forgets the second, because the second file isn't in front of it. Co-located, that's a single edit in a single file — change the function, change its type, done, nothing left stale.

There's a human cost too (every type change is a context switch to a file that grows monotonically and becomes a merge-conflict magnet), but the AI angle is what tips it decisively.

## What I'd actually do

Think in three tiers rather than one bucket:

1. **Type used by a single module → co-locate it.** Define it in the same file as the function/component/service that owns it, or right next to it. This is where most of your 400 lines probably belong. When Claude opens that file, the type is right there — full context, no lookup, edits stay in sync.

2. **Type shared across a feature → lift it to a feature-level file.** If three files in `checkout/` share a `CartLine`, a `checkout/types.ts` is the right home — shared, but still local to the code that uses it. The boundary is "who genuinely shares this," not "all types everywhere."

3. **Truly global primitives → keep a small central file.** A handful of app-wide types (a `UserId`, a shared `ApiError`, core domain enums) can stay central. The key word is *small*. This is a curated set that's genuinely cross-cutting, not the default dumping ground.

The test for each type: **can it be understood in isolation, and who actually needs it?** If only one module touches it, co-location wins outright. If several do, lift it just far enough to be shared — no further.

## Practical migration

No need for a big-bang refactor. Let it drift:

- New types go next to their owner from now on.
- When you touch an existing type, move it down to where it's used as part of that change.
- Periodically grep for what's left in `types.ts` — if a type has one importer, relocate it; if it has many across features, it's a real shared type, leave it (or feature-scope it).

You'll likely find `types.ts` melts down to a short list of genuinely global types, which is exactly what you want it to be.

## One nuance

Don't over-correct into scattering. If a cohesive file already keeps logic and its types together and runs a couple hundred lines, that's *good* — cohesion beats line count, and a self-contained file is the best possible prompt for an agent. The goal isn't "types everywhere," it's "types live with the code that owns them, lifted only when genuinely shared." That keeps your single-source-of-truth guarantee while making each file something Claude can edit correctly without chasing a definition it'll never open.

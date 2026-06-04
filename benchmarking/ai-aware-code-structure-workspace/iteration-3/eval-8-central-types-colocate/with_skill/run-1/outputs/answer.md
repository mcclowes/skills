# On the central `types.ts`

Short version: it felt clean, but a single central types file is working against you now that Claude Code does most of the editing. I'd move most of those types next to the code that owns them and keep only the genuinely global primitives central.

## Why the central file hurts in an AI workflow

The thing to design around is that AI agents are remarkably reluctant to open files that aren't already in front of them. A human jumps to `types.ts`, reads the shape, jumps back, no friction. An agent in your service file often just... doesn't. It either burns context chasing the definition or, more often, guesses the shape of a type and edits confidently wrong.

A central `types.ts` is the textbook version of "the sibling the agent won't open." Every component and service depends on it, but none of them contain it. So the most common failure mode is:

- You ask Claude to change a field on some entity.
- It edits the component or service that uses the type.
- It never opens `types.ts`, so the type definition and the code drift apart — or it edits the wrong half and the other half is now stale.

You've split one logical change ("this thing now has a `status` field") across two files, on exactly the axis where the agent is weakest. That's the opposite of what you want.

There's a second, quieter cost: a 400-line types file that *everything* imports is low signal-to-noise for the agent. When it does pull that file in, it's loading 380 lines of irrelevant types to find the one it needs.

## The rule I'd use

**Define a type next to the code that owns it.** Changing the code and changing its type then becomes one edit in one file — the agent sees both at once and keeps them in sync.

"Single source of truth" is still intact, by the way. It means each type is defined *once*, not that all definitions live in *one file*. Those are different things, and only the first one actually matters.

Concretely, three tiers:

1. **Type used by one module** → co-locate it in that module's file. This is most of your 400 lines, I'd bet.
2. **Type genuinely shared across a feature** → lift it to a feature-level file (e.g. `features/billing/types.ts`) that the feature's files sit next to.
3. **Truly global primitives** (a handful — `UserId`, `ISODateString`, a couple of core domain enums) → keep them central. These are rarely edited and universally needed, so the central location is fine and even helpful.

The test for each type: *if I change the code, do I almost always change this type in the same edit?* If yes, co-locate. If the type is stable and shared by many unrelated modules, central is fine.

## How I'd approach the migration

You don't need to do this in one go, and you shouldn't.

- Start by moving types that are imported by exactly one file — pure wins, no ambiguity.
- Then group the feature-clustered ones into feature-level type files.
- Whatever's left after that is your real "global" set. If it's still big, that's a signal those types are doing too much, not that they belong together.

One caveat worth naming: don't over-correct into a per-type file explosion. The goal is co-location with the *owning code*, not a new scattered pile of tiny type files. A type lives in the `.ts`/`.tsx` file of the thing it describes, not in its own file next door.

## Bottom line

Co-locate. Move single-consumer types into their owning files, lift shared ones to feature level, keep a small central file for true global primitives. The central `types.ts` optimised for a reader browsing the whole codebase; co-location optimises for an agent making a focused change without chasing a definition across a boundary it won't cross. Given that Claude Code does most of your edits now, that's the trade-off that matters.

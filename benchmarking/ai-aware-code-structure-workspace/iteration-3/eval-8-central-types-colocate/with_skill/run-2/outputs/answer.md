# Move most types next to the code that owns them

Short version: the central `types.ts` felt clean for humans, but it works against you now that Claude Code is your main editor. I'd colocate the bulk of those types and keep only a small genuinely-global core central.

## Why the single file hurts in an AI workflow

The thing that made it feel clean — "every type in one place" — is exactly the thing that bites an agent. AI tools are weirdly reluctant to open adjacent files. They work with what's in front of them and make confident edits based on the open file. A human navigating your codebase glances at `types.ts` without a second thought; an agent editing a service often just doesn't go look, and either guesses the shape of a type (and edits confidently wrong) or burns context pulling in all 400 lines when it needs ten of them.

There's also a sync failure mode that shows up constantly: the agent changes a function and needs to change its type too. When the type lives in the same file, that's one edit in one file. When it lives in `types.ts`, that's two files — and the agent reliably does the first and forgets the second. You end up with types that have quietly drifted from the code they describe.

## "Single source of truth" doesn't mean "one file"

This is the misread worth correcting. Single source of truth means each type is *defined once* — no duplicate `User` interfaces scattered around. It does not mean every definition lives in the same physical file. You keep the SSOT guarantee perfectly well by defining each type once, next to its owner. The file count is irrelevant to that property.

## What I'd actually do

Sort the ~400 lines into three buckets:

1. **Owned by one module** — a type only its service or component uses, or a type that always changes alongside one piece of code. Move it next to that code. This is most of your file. Changing the code and its type becomes a single, local edit.

2. **Shared by a few modules in one feature** — lift it to a `types.ts` *within that feature's folder*, not the global one. It sits near everything that uses it and the blast radius is visible.

3. **Truly global primitives** — `UserId`, `ISODateString`, a core `User` that genuinely flows through the whole app. Keep these central. There usually aren't many, and for these the central file *is* the right abstraction.

The test for each type: **can the type be understood next to the code that uses it, by an agent that won't open another file?** If yes, colocate. If several genuinely-independent modules share it, lift it just to the level they share.

## Worth being honest about

- This is more import statements and a bit more friction when you *do* want to eyeball "all our types at once." In an AI-edited codebase that trade is worth it — the agent rarely wants the whole catalogue, it wants the few types relevant to the file it's in, and colocation delivers exactly that.
- You don't have to do it as one big-bang refactor. Move types as you touch the code, and stop adding new types to the central file from today. Most of the pain comes from the file growing, so capping its growth gets you most of the benefit immediately.
- One nuance: a 400-line types file isn't catastrophic the way a 400-line tangled component is — types are low-noise and an agent tolerates them. So this is a "lean toward colocating," not an emergency. The drift-and-sync problem is the real reason to act, not the line count.

So: not a good idea to keep everything central, but don't overcorrect into zero shared types either. Colocate by ownership, lift to feature level when shared, keep a small global core.

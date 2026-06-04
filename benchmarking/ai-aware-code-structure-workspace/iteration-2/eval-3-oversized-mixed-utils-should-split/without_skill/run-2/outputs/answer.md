# Split it — but the reason isn't "550 lines is too big"

Short version: yes, split it, but not because of the line count. Split it because the file has no coherent identity. The "big files are fine for AI" advice is real, but it's being misapplied here.

## What's actually true about big files and AI

The advice you've read is roughly correct: a large, *cohesive* file is fine — sometimes better — for an AI agent. If everything in a 1,500-line file is one tightly-related concern (say, a single state machine, or one parser), an agent benefits from seeing it all at once. There's no import-chasing, the full context fits in one read, and edits stay local. Line count alone is a weak signal. Don't refactor purely to hit some magic number.

The catch: that argument only holds when the contents belong together. Your `helpers.ts` is the opposite case. By your own description it's five unrelated concerns that "just landed" in the same place:

1. Date formatting
2. Currency formatting
3. A fetch wrapper
4. Form-validation predicates
5. Array/object utilities

You even noted they don't call each other. That's the tell. This isn't a big cohesive module — it's a junk drawer that happens to be one file. The problems with a junk drawer are real for both humans and agents, and none of them are fixed by the "big files are fine" reasoning.

## Why the junk drawer hurts, specifically for AI agents

- **Every importer looks like it depends on everything.** An agent (or a human, or a static analyzer) sees `import { formatDate } from './helpers'` and can't tell from the dependency graph that this file doesn't also drag in your fetch wrapper. When an agent reasons about blast radius — "what could break if I touch helpers.ts?" — the honest answer is "anything that imports it," which is your whole app. Splitting gives you honest, narrow dependency edges.

- **Retrieval gets noisier.** When an agent searches the codebase for "currency formatting," a file named `helpers.ts` is a worse hit than `currency.ts`. The filename is a free, high-signal label. A grab-bag name throws that signal away and forces the agent to read 550 lines to find the 15 it needs.

- **Edits have a wider perceived footprint.** Touching one function in a shared mega-file means every tool, reviewer, and agent treats the change as touching the shared utilities surface. Smaller files scope the change visibly.

- **Cohesion, not size, is what an agent actually wants.** The thing that makes a file easy to load into context and reason about is that it's *about one thing*. Five things in one file is five times the irrelevant context on every read.

So the real principle isn't "small files good, big files bad." It's: **a file should have one clear reason to exist.** Yours has five.

## What I'd actually do

Split by concern, one file per cohesive group:

```
utils/
  date.ts          // date formatting
  currency.ts      // currency formatting
  validation.ts    // form-validation predicates
  array.ts         // array/object utilities (or object.ts if it grows)
  http.ts          // the fetch wrapper
```

A couple of notes on the grouping:

- The **fetch wrapper is the odd one out** and the most worth separating first. It's the only thing here with real behavior, dependencies (network, error handling, maybe auth/headers), and likely the only thing you'd want to mock in tests or swap later. Keeping it tangled with pure formatting helpers is the worst pairing in the bunch. If you only have appetite for one split, pull `http.ts` out.
- Date and currency are both "formatting" — fine to keep separate, fine to fold under a `format/` folder if you prefer. Don't overthink it.
- Validation predicates often grow fast once you start adding rules. Giving them their own home now pays off.

## Don't pay a migration tax you don't have to

Your real concern is probably "it's imported all over the app." Two ways to handle that:

1. **Move the functions, then re-export from the old path.** Keep `helpers.ts` as a barrel that re-exports from the new files. Nothing breaks, every existing import keeps working, and you can migrate call sites lazily (or never). This is the safe, zero-risk move.

2. **Move and update imports in one pass.** A find-and-replace or codemod across the app, or honestly just an agent with a working build to check against, can do this in minutes. This is cleaner long-term because you delete the barrel and the indirection.

I'd do (1) today to de-risk, then opportunistically migrate toward (2). Avoid leaving a permanent barrel that re-exports everything — that recreates the "imports the world" problem at the import-statement level even if the files are split.

## The one case where I'd say leave it

If this file were genuinely cohesive — one domain concept, functions that call each other, shared types — I'd tell you to leave it at 550 lines and not split on principle. Size isn't the enemy. But that's not your file. Yours fails the "one reason to exist" test, and that's the test that matters for both humans and agents.

**Bottom line:** split by concern (5-ish small files), pull the fetch wrapper out first, and use a temporary re-export barrel so nothing breaks while you migrate. Ignore the line count — follow the cohesion.

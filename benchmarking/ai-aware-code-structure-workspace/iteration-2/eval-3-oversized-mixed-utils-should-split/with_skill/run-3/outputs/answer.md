# Split it — but for the right reason

The "big files are fine for AI now" take is half right, and it's leading you to the wrong conclusion here. Let me untangle it.

## Why the "big files are fine" advice doesn't apply

The reason that advice exists: the old "if it doesn't fit on a screen, split it" rule was calibrated for human scrolling. Agents handle larger files fine, and a cohesive file that keeps tightly-coupled code together often beats two smaller files that are meaningless apart — because agents are reluctant to look at adjacent files, so a self-contained file is a better prompt than a fragmented one.

But that argument only holds for files that are **one coherent concern**. The benefit of keeping a big file together is *cohesion* — logic and its rendering, a function and the types it needs, things that get changed together and need each other for context.

Your `helpers.ts` is the opposite. By your own description: date formatting, currency formatting, a fetch wrapper, form-validation predicates, array/object utilities — and **they don't call each other**. There's no cohesion to preserve. It's not a coherent unit that happens to be long; it's five unrelated units that happen to share a file. The "keep it together" logic earns you nothing because there was never anything to keep together.

## Why this file actively hurts an agent

When an agent opens `helpers.ts` to tweak one date formatter, it pays for all 550 lines — currency, fetch, validation, the lot — in context tokens and attention. That's pure noise relative to the task. Signal-to-noise is the whole game for machine readability, and a grab-bag util file is the worst case: maximum surface area, minimum relevance per token. You're past the ~300-line mark where signal-to-noise becomes the problem, *and* you're spanning several concerns. Both triggers for splitting are present.

There's also no cross-file-context cost to worry about here, which is normally the thing that makes me cautious about splitting. The risk with splitting is leaving files that only make sense when read together — a "dumb" file whose props or types live in a sibling the agent won't open. Independent utilities have none of that. Each function is props-in/output-out with no shared state. They pass the decision test cleanly:

> **Can this concern be understood in isolation?**

Yes — emphatically — for every group here. That's the green light to split.

## How to split it

Group by concern, one file per cohesive area:

```
utils/
  date.ts          // date formatting
  currency.ts      // currency formatter
  validation.ts    // form-validation predicates
  collection.ts    // array/object utilities
  http.ts          // the fetch wrapper
```

A few notes:

- **The fetch wrapper is the one to scrutinise.** Formatting and validation are genuinely pure and trivially isolatable. A fetch wrapper sometimes drags in config, error types, or auth concerns. If it's truly thin and standalone, `http.ts` is fine. If you find it wants types or config from elsewhere, that's a signal to co-locate it with whatever it's coupled to rather than stranding it.
- **Don't over-split within a group.** Keep all the date helpers in `date.ts` even if it's a few of them — they're a coherent concern, and splitting one function per file would just recreate the fragmentation problem in miniature. Let each file grow to a couple hundred lines while it stays on-topic.
- **Reach for abstractions, not just relocation, where it pays.** Splitting moves code; it doesn't reduce what an agent must understand to use it. Your utilities are already well-abstracted (a named function with a clear signature *is* the abstraction — an agent reads `formatCurrency()` at the call site and proceeds without reading the body). So here, plain grouping into files is the right and sufficient move. No need to invent hooks or wrappers.

## The import churn

It's imported all over the app, so the mechanical cost is real but mild. Two clean options:

1. **Update imports directly** — a find-and-replace / codemod across call sites. Cleanest end state, and your tooling (or an agent, ironically) makes this cheap.
2. **Keep `helpers.ts` as a barrel** that re-exports from the new files during a transition, then migrate call sites and delete it. Lower blast radius, but don't let the barrel become permanent — re-exports reintroduce the indirection you're trying to remove.

I'd do (1) if the codebase is small enough to sweep in one pass, (2) if it's large or you want to land it incrementally.

## Bottom line

Leave it as one file only if it were one concern. It's five. Split by concern into focused, independently-understandable files — each passes the isolation test, there's no cross-file coupling to lose, and you cut the per-task noise an agent has to wade through. The "big files are fine" advice protects *cohesion*; it was never a licence to keep a junk drawer.

# Should you leave `helpers.ts` as one 550-line file?

Short answer: split it. Not because 550 lines is "too big" in the abstract, but because of what's *in* those lines. The "big files are fine for AI now" claim is half-true, and it doesn't apply to your situation.

## What the "big files are fine" argument actually says

There's a real point buried in that advice. Long files with **high cohesion** — where everything is about one thing and the pieces genuinely belong together — are often easier for an agent (and a human) to work with than the same code shattered across fifteen tiny files with deep import chains. Splitting has a real cost: more files to discover, more indirection to follow, more places to look. A 600-line module that models one coherent domain concept can be perfectly fine, and chopping it up "because 600 is a big number" is cargo-cult refactoring.

So the line-count heuristic is genuinely outdated. That part is correct.

## Why it doesn't rescue your file

Your `helpers.ts` is the exact opposite of the high-cohesion case. By your own description it's:

- date formatting
- a currency formatter
- a fetch wrapper
- form-validation predicates
- array/object utilities

Five unrelated concerns that *don't call each other*. The file has no organising principle beyond "stuff we needed." That's the worst-case shape for both humans and agents, and the reasons are concrete, not aesthetic:

**1. It's a context magnet.** Because it's "imported all over the app," almost any task pulls this file into context. An agent fixing a date bug now has the fetch wrapper, the validators, and the array utils sitting in its window, burning tokens and adding noise that has nothing to do with the task. Smaller, purpose-named files let the agent (and your editor's go-to-definition, and grep) load only what's relevant.

**2. The import graph is lying.** Everything that uses *one* helper imports from a module that also contains four unrelated things. You can't tell from the dependency graph what actually depends on what. A component that only formats currency looks, to any tooling, like it depends on your fetch layer. This wrecks tree-shaking, dead-code detection, and any reasoning ("what breaks if I change this?") an agent tries to do.

**3. Misleading retrieval.** When an agent searches for "validation" or "format," it lands in a grab-bag file and has to mentally filter. Good file *names* are a huge, cheap signal for retrieval. `helpers.ts` tells the reader nothing; `validation.ts` tells them exactly what they'll find.

**4. Blast radius and merge churn.** Five concerns in one file means five reasons for it to change, five teams/PRs touching the same file, and a higher chance of conflicts and accidental coupling. Each unrelated edit risks the others.

None of these problems are about the number 550. They'd be just as bad at 300 lines and only slightly better at 200. The issue is **mixed, low-cohesion concerns in a high-fan-in module.**

## What I'd do

Split by concern, one file per coherent group, named for what it is:

```
src/utils/
  date.ts          // date formatting
  currency.ts      // currency formatter
  http.ts          // the fetch wrapper
  validation.ts    // form-validation predicates
  collections.ts   // array/object utilities
```

Concrete steps:

1. **Move, don't rewrite.** Cut each group into its own file verbatim. No logic changes in this PR — that keeps the diff reviewable and the behaviour identical.
2. **Update imports.** Since it's imported everywhere, let the tooling do it: your IDE's "move symbol" refactor will rewrite call sites, or do a mechanical find-and-replace. This is the only tedious part, and it's a one-time cost.
3. **Decide on a barrel — carefully.** You *can* add an `index.ts` that re-exports everything so existing `import { foo } from '../helpers'` paths keep working. It makes the migration painless. But a barrel re-introduces the "import one thing, pull in everything" problem for bundlers and for context loading, so I'd treat it as a temporary bridge and migrate call sites to import directly from `date.ts`, `currency.ts`, etc. If you keep the barrel long-term, at least you've fixed the *authoring* clarity even if the import surface stays wide.
4. **Add tests per file as you go.** These are pure, dependency-free utilities — ideal for unit tests. If they're untested today, a focused `date.test.ts` next to `date.ts` is a cheap win and makes the split safe.

## On the fetch wrapper specifically

One thing worth calling out: the `http.ts` wrapper is the odd one out. The other four are pure, synchronous, no-dependency utilities. The fetch wrapper has real behaviour — error handling, maybe auth headers, base URLs. It's the most likely to grow and the most likely to need its own tests and types. Definitely give it its own home, and don't be surprised if it later wants to become a small folder of its own.

## Bottom line

"Big files are fine for AI" is true for **cohesive** files and false for **grab-bag** files. Yours is the grab-bag case — five concerns that share nothing but a filename. Split it by concern into well-named files. The win isn't satisfying a line-count rule; it's that every future task, human or agent, loads less irrelevant context, gets an honest dependency graph, and finds code by searching for what it does. It's a mechanical, low-risk refactor with a clear payoff. Do it.

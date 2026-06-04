# Review: UserBadge folder layout

Short version: this is over-split. For a single small component, splitting one logical unit across five files is a net negative — and that's *especially* true in a codebase where AI assistants do a lot of the editing. I'd collapse it down to one or two files.

## What you have

```
UserBadge/
  index.ts                  # re-export
  UserBadge.view.tsx        # JSX only
  UserBadge.logic.ts        # 40 lines
  UserBadge.styles.ts       # styles
  types.ts                  # types
```

Each file is small and single-purpose, which sounds like clean architecture. But "single-purpose file" and "single-responsibility component" aren't the same thing. A `UserBadge` *is* the unit of responsibility here. Slicing it by technical layer (view / logic / styles / types) splits one cohesive thing across five files for no real gain at this size.

## Why this is the wrong default for an AI-heavy codebase

The instinct that "smaller files are easier for an AI to handle" is backwards for components this small. Here's the reasoning:

1. **Context assembly cost.** To make almost any change to this badge — tweak the rendered markup, adjust the logic that feeds it, restyle it — an assistant (or a human) has to open and hold 3-5 files in its head simultaneously. The view doesn't make sense without the logic; the logic doesn't make sense without the types. You've guaranteed that the *minimum* working set is the whole folder. A single 80-120 line file would fit in one read and one edit.

2. **Edits fan out across files.** Add a prop and you're touching `types.ts`, `UserBadge.logic.ts`, and `UserBadge.view.tsx` in one logical change. That's three edits an agent has to keep consistent, three chances to leave something half-updated, and more diff surface to review. Co-located code means one edit in one place.

3. **The split is by *layer*, not by *concept*.** Good module boundaries separate things that change for different reasons. View, logic, styles, and types for one badge all change together — when the badge changes. So the boundaries you've drawn don't actually isolate anything; they just add navigation hops. This is the classic "horizontal" split that reads as tidy but couples everything across the seam.

4. **40 lines of "logic" is not a module.** A 40-line logic file is below the threshold where extraction pays for itself. If that logic is a hook or a couple of pure helpers, it lives happily at the top of the component file or in a sibling only once it's *reused or independently tested*.

## When splitting *does* earn its keep

To be clear, the layered split isn't always wrong. It starts to pay off when:

- The view file is genuinely large (say, a few hundred lines of JSX) and skimming it is painful.
- The logic is non-trivial, reused elsewhere, or has its own test suite — then a `useUserBadge` hook or a `userBadge.utils.ts` is justified, because it's now a real reusable unit.
- The types are shared across multiple components/modules — then they belong in a shared `types.ts`, not a per-component one.
- Styles are heavy and you want them out of the way (and even then, co-located styles are fine until they're large).

The trigger is *size and reuse*, not a blanket "one concern per file" rule applied uniformly to every component regardless of weight.

## What I'd do

Collapse to a single file:

```
UserBadge/
  index.tsx     # types + logic + styles + component, in that reading order
```

or, if you keep the `index.ts` barrel convention:

```
UserBadge/
  index.ts          # re-export
  UserBadge.tsx     # everything
```

Order it top-to-bottom so it reads like a story: types → small helpers/hook → styles → the component that uses them. An assistant opening this file sees the whole feature in one pass and can edit it in one place.

Drop the per-component `types.ts` unless those types are shared elsewhere. Keep `index.ts` only if your import conventions rely on the barrel — otherwise even that's optional ceremony.

## The general rule

Optimise for **the size of the working set needed to make a change**, not the size of individual files. For an AI editor, the cost is "how many files must I read and keep consistent to do this safely," and co-location minimises exactly that. Split when a file gets genuinely large or a piece becomes independently reused/tested — let it grow first, then divide along real conceptual seams. Don't pre-split a small component along technical layers; that's structure that looks clean in a file tree and costs you on every edit.

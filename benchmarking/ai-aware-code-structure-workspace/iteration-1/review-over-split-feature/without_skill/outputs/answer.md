# Review: UserBadge feature folder layout

Short version: this is over-split, and "we use AI assistants heavily" is an argument *against* this layout, not for it.

## The structure you have

```
UserBadge/
  index.ts              # re-export
  UserBadge.view.tsx    # JSX only
  UserBadge.logic.ts    # 40 lines
  UserBadge.styles.ts
  types.ts
```

Five files for one small component. The driving principle here seems to be "one responsibility per file" taken to the file-system level. That sounds disciplined, but it's solving a problem you don't have yet and creating a few real ones.

## Why this isn't great, especially with AI assistants

I'd challenge the assumption that more files = more AI-friendly. The opposite tends to be true.

**It fragments context.** To understand or change `UserBadge`, an AI assistant (or a human) has to open and hold 4-5 files in working memory: the view, the logic, the types, the styles, plus the barrel. A single `UserBadge.tsx` of ~80-120 lines fits in one read, one context window, one diff. Splitting forces extra tool calls / file reads just to reconstruct what was one cohesive unit. For AI workflows specifically, fewer round-trips and self-contained files are a feature.

**The seams are artificial.** `view.tsx` (just JSX) and `logic.ts` (40 lines) are not independently meaningful. The JSX needs the logic's return values; the logic exists only to feed the JSX. You've separated two halves of one thought. A real seam is one where each side has value or reuse on its own — that's not the case here.

**Edits sprawl across files.** Adding one prop to `UserBadge` can touch `types.ts`, `logic.ts`, `view.tsx`, and `styles.ts`. That's four files dirtied for a trivial change — more diff noise, more chance of an AI assistant editing one file and forgetting a sibling, harder review.

**`logic.ts` is a smell at 40 lines.** A presentational badge with 40 lines of separate logic suggests either (a) the logic is trivial and shouldn't be its own file, or (b) it's doing something non-trivial (data fetching, derivation) that may belong in a hook or a shared util, not a component-private `.logic.ts`.

## What I'd do instead

Collapse to a single file. Co-locate types and styles, extract only when there's a concrete reason.

```
UserBadge/
  UserBadge.tsx         # component, local types, styles
  UserBadge.test.tsx    # test alongside
  index.ts              # optional barrel
```

Or, if you prefer flat:

```
UserBadge.tsx
UserBadge.test.tsx
```

Guidelines I'd apply:
- **Default to one file per component.** Keep types, the small bit of logic, and styles inline.
- **Split only on a real trigger**, not preemptively. Good triggers: the file genuinely gets long (say 200+ lines); a type/util is *reused* elsewhere (move it to a shared location, not a sibling file); the logic becomes a reusable hook (`useUserBadge`); styles are large enough to be noise (and even then, prefer a `.module.scss`/`.styles` split, not splitting JSX from logic).
- **Drop the `index.ts` barrel** unless you actually need a stable public import path. Per-component barrels add indirection and are a common source of circular-import and tree-shaking issues — and they're another file to open.
- **`types.ts` only earns its place** when types are shared across multiple files in the folder. For one component, inline them.

## When the split-everything approach *is* defensible

To be fair: per-file separation can make sense when components are large, when a design system enforces a rigid contract, or when styles/types are genuinely shared and reused. If `UserBadge` is an outlier and the rest of the codebase has fat, complex components, a consistent convention has some value. But applying it to a small badge is cargo-culting the convention past the point where it pays off.

## Bottom line

For a small, single-purpose component, five files is over-engineering. Co-locate into one `UserBadge.tsx` (plus a test), and split out pieces only when a real reason appears. This is *more* AI-friendly, not less: self-contained files mean fewer reads, tighter context, and edits that don't sprawl across siblings.

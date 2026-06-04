# Review: UserBadge folder structure

Short version: this is **over-split** for what it is. I'd collapse it. For a component this small, the five-file layout costs you more than it gives you, and that cost is *higher*, not lower, when AI assistants are doing most of the editing.

## What you have

```
UserBadge/
  index.ts              # re-export
  UserBadge.view.tsx    # JSX only
  UserBadge.logic.ts    # 40 lines
  UserBadge.styles.ts
  types.ts
```

Five files for a single badge component. Each file is "small and single-purpose" — but that's the trap. Small and single-purpose is a virtue for a *function*, not automatically for a *file*. Files have a fixed overhead (a tab, an import line, a mental "where does this live" lookup) that doesn't shrink just because the contents are tiny.

## Why this is the wrong tradeoff for an AI-heavy workflow

The intuition that "small files help the AI" is backwards here, and it's worth being explicit about why.

1. **The unit of comprehension is the feature, not the file.** When you (or an agent) change UserBadge, you almost always need the props, the rendering, and the behaviour together. A `view` that's "just JSX" can't be understood or safely edited without the `logic` and `types` open beside it. You've separated things that change together, which is the opposite of cohesion. Splitting by *kind of code* (view / logic / styles / types) rather than by *feature* creates artificial seams that nearly every edit has to cross.

2. **More files = more context to load, not less.** An agent editing this has to open and reason across 4–5 files to make one coherent change, plus follow the `index.ts` indirection to figure out the real entry point. A single ~120-line file is one read, fully in context, with the data flow visible top to bottom. Token budget and attention both go further when related code is co-located.

3. **More surfaces to keep in sync.** Logic that references a type means a change can ripple across `logic.ts`, `types.ts`, and `view.tsx`. Each split is a place an agent can make a locally-correct edit that's globally inconsistent (e.g. adds a prop in `view` but forgets `types`). Co-location makes that class of mistake structurally harder.

4. **The "single-purpose file" smell.** `UserBadge.logic.ts` at 40 lines, `view` that's "just JSX," and a `types.ts` for one component's props are all signs the split is dogmatic rather than load-bearing. None of these files is independently reusable or independently testable in a way that earns its own file.

## What I'd actually do

Collapse to **one file**, with an `index` only if your import conventions require a folder:

```
UserBadge/
  index.ts        # only if you import folders elsewhere; otherwise drop the folder entirely
  UserBadge.tsx   # types + logic (hook) + styles + JSX, in that reading order
```

Or, if you don't have a folder-import convention, just `UserBadge.tsx` flat. Order it so it reads top-to-bottom: types → the hook/logic → the component → styles (or styles last, whatever your house style is). One scroll, one mental model.

Keep tests alongside: `UserBadge.test.tsx`. That's the one "extra" file worth having, because tests genuinely are a separate concern with a separate audience.

## When the split *would* be justified

I'm not arguing files-of-one-kind are always wrong — there are real triggers, you just haven't hit them:

- **Styles** earn their own file when there's a lot of them, or your styling lib mandates it (e.g. CSS/SCSS modules — which, per your usual stack, you'd want as `UserBadge.module.scss`, not a `.styles.ts`).
- **Logic** earns its own file when it's a genuinely reusable hook consumed by more than one component, or when it's big/complex enough that mixing it with JSX hurts readability (think 150+ lines, real branching).
- **Types** earn their own file when they're shared across the feature boundary, not when they're one component's local props.

The rule of thumb: split when a piece has its *own reason to change* and its *own audience*. Right now all five files share one reason to change (the badge) and one audience (whoever edits the badge). That's a single module wearing five hats.

## Bottom line

Merge it. One file (plus a colocated test, plus an `index` only if your import style needs it). It'll be easier for both humans and agents to read, edit, and keep consistent. Re-split later *per-concern, only when a specific concern actually grows a reason to live on its own* — not preemptively. Premature file-splitting is the structural cousin of premature abstraction, and AI assistants don't change that calculus; if anything they reward co-location more, because their effectiveness is bounded by how much relevant context sits in one place.

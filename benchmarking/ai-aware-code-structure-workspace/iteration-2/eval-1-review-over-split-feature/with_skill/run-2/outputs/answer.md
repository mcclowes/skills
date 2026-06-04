# Review: UserBadge folder structure

Short version: this is over-split for an AI-heavy codebase. Each file is small and single-purpose, which feels clean, but you've optimised for a metric ("one concern per file") that doesn't actually serve the readers you care about — especially the AI ones.

## The problem

You've got five files for what is almost certainly a small component:

```
UserBadge/
  index.ts              barrel re-export
  UserBadge.view.tsx    just JSX
  UserBadge.logic.ts    40 lines
  UserBadge.styles.ts
  types.ts
```

The issue isn't file count for its own sake — it's that the split forces cross-file context for a unit that is tiny enough to belong together.

The test that matters isn't "is this a separate concern?" It's **"can this concern be understood in isolation?"** Run it on each file:

- **`UserBadge.view.tsx` (just JSX)** — this is the big one. A render file whose props are shaped in `logic.ts` and whose types live in `types.ts` cannot be understood or safely edited on its own. To change the markup, an agent needs to know the prop shape, which is two files away.
- **`UserBadge.logic.ts` (40 lines)** — 40 lines is small. If this logic only exists to feed the view, the two halves are meaningless apart. Splitting them just creates two files that each require the other.
- **`types.ts`** — for a single small component, the types are part of understanding both the logic and the view. Pulling them out adds a third lookup.

This matters more with AI in the loop because agents are markedly reluctant to open adjacent files. A human glances at the sibling and holds the model across files without thinking. An agent works with the open file and makes confident edits that break because it never checked how a prop was shaped two files over. Every split here manufactures exactly that failure mode: the agent lands in `view.tsx`, can't see the prop shape, and guesses.

"Small and single-purpose" is the human-era reflex ("if it doesn't fit on a screen, split it"). Agents handle a cohesive 150-line file fine — better, in fact, than four 40-line files that are meaningless apart. Cohesion beats line count until you're somewhere north of ~300 lines, and you're nowhere near that.

## What I'd do instead

**Collapse view + logic + types + styles into `UserBadge.tsx`.** One self-contained file an agent can open and fully understand: the markup, the props that feed it, the types, the styles, all in front of it. For a component this size that's almost certainly well under 100 lines — high signal-to-noise, zero cross-file lookups.

```
UserBadge/
  index.ts        (optional — see below)
  UserBadge.tsx
```

A few refinements:

- **Styles** can reasonably stay separate *if* they're genuinely standalone (a styled-components / token file that reads fine alone and rarely changes with logic). Styles are the one piece here that often passes the isolation test. But if they're trivial, fold them in too.
- **`index.ts`** as a pure barrel re-export is low-cost but also low-value for a single component. If your import convention needs it, keep it; otherwise drop it and import from `UserBadge.tsx` directly.
- If `UserBadge.tsx` later grows and one part earns a *real* interface — say the logic becomes a reusable `useUserBadge()` hook with a clear contract — extract that. An abstraction beats a file split, because the call site (`const badge = useUserBadge(user)`) tells the agent enough to proceed without reading the internals. Relocating code into `logic.ts` doesn't do that; it just moves the code while leaving the coupling.

## When the current layout *would* be right

If `UserBadge` were genuinely large and complex — a few hundred lines, real orchestration, styles that stand fully on their own — splitting along these lines starts to pay off, because each file crosses the ~300-line signal-to-noise threshold and the boundaries become ones each side can survive alone. At 40 lines of logic, you're not there.

## Bottom line

Don't split for "single-purpose" as a reflex. Split when a piece either (a) can be understood in isolation, or (b) earns a real abstraction with an interface. A purely-presentational view file whose props are shaped elsewhere fails (a), and a 40-line logic file feeding one view doesn't yet warrant (b). Merge them into one `UserBadge.tsx`, keep styles separate only if they truly stand alone, and reach for a hook (not a new file) the day one part earns one.

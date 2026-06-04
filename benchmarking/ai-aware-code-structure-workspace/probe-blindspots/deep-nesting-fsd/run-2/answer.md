For a feature this size, no — the full FSD layering is over-structured, and the fact that you edit almost entirely through Claude Code makes it actively worse rather than neutral. I'd push back on it as your default.

## Why not here

FSD's `api / model / ui / lib / config` split is built for *large* slices where each layer has enough mass to justify its own home, and where the main reader is a human who navigates files intuitively. Yours is three concrete things: a plan picker, a checkout call, an invoices list. If you impose the full layering, you get a tree like:

```
billing/
  api/        checkout.ts, invoices.ts, index.ts
  model/      types.ts, store.ts, index.ts
  ui/         PlanPicker.tsx, Checkout.tsx, InvoicesList.tsx, index.ts
  lib/        format.ts, index.ts
  config/     plans.ts, index.ts
```

That's ~15 files where the actual code might be 400-500 lines total. Each file is tiny, and — this is the key part — most of them are *meaningless on their own*. `PlanPicker.tsx` renders props whose shape lives in `model/types.ts`; the checkout button calls something in `api/checkout.ts`; the plan list it maps over comes from `config/plans.ts`. A human flips between those four files without thinking. An agent in the open file won't — it'll confidently edit `PlanPicker.tsx` against an assumed prop shape and break against the real one two folders over.

So the layering doesn't just fail to help the agent, it directly hits the thing agents are worst at: cross-file context that they won't proactively go and read. You'd be paying the coordination cost of the structure and getting buggier edits in return.

The `index.ts` barrels make this worse on two fronts. They add a layer of indirection the agent has to resolve before it even finds the real code, and they cost tokens for zero comprehension benefit. Barrels earn their keep when you're managing a public API surface across a big module boundary — not for re-exporting three components within one small feature.

## What I'd do instead

Structure around the three things the feature actually *is*, and let each one be self-contained:

```
billing/
  PlanPicker.tsx      // the picker + its config/plan data + local logic
  InvoicesList.tsx    // the list + its fetch/render
  checkout.ts         // the checkout call (a real abstraction: useCheckout / startCheckout)
  types.ts            // shared types, only if 2+ files genuinely need them
```

Four files, each readable in isolation. An agent asked to "change the plan picker" opens one file and has everything: the markup, the plan data, the local state. That's a far better prompt than reconstructing the feature from five folders.

Two principles doing the work here:

- **Co-locate things that change together.** The plan data and the picker that renders it are always edited in the same breath — keep them in one file so the agent works from a complete picture. Same for the invoices fetch and the invoices list.
- **Reach for an abstraction, not a folder.** The one place a real boundary pays off is the checkout call. Wrap it as `useCheckout()` / `startCheckout()` with a clear signature. Now the call site reads `const { start } = useCheckout()` and the agent knows enough to proceed without opening the implementation. That's a genuine reduction in required context — which splitting a file into a `api/` folder never gives you; it just relocates the code.

## Where to draw the lines

- Let these files grow. A cohesive 150-200 line `PlanPicker.tsx` that holds its data, state, and markup together beats three 60-line files that are individually meaningless. Agents handle a few hundred lines fine; split when signal-to-noise actually drops (past ~300, or when a file clearly covers two unrelated concerns), not on reflex.
- Pull out a separate file the moment a piece is **purely presentational** — props in, JSX out, no side effects. A dumb `InvoiceRow` is self-documenting and a great standalone file. That's the split that helps the agent rather than starving it.
- Only hoist a shared `types.ts` once two files genuinely depend on the same type. Before that, keep the type next to the code that owns it.

## The honest caveat

If your codebase *already* uses strict FSD everywhere and tooling/lint enforces it, consistency has real value — don't make billing the one weird island. In that case, follow the house pattern but collapse the empty layers: skip `lib/` and `config/` when there's nothing in them, and drop the within-feature barrels. And this is a moving target — as agents get better at navigating across files, aggressive layering gets cheaper. For the tools you have today, structure for the agent that won't look around: fewer, fatter, self-contained files.

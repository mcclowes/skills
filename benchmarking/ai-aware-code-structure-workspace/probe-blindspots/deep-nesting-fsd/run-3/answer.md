No — for a feature this small, the full FSD layered structure is over-engineering, and it actively works against you given that Claude Code does most of your editing.

## What you're describing

```
billing/
  api/      index.ts + small files
  model/    index.ts + small files
  ui/       index.ts + small files
  lib/      index.ts + small files
  config/   index.ts + small files
```

For "a plan picker, a checkout call, and an invoices list," that's five folders and five barrel files wrapping maybe 200-300 lines of actual code. The structure weighs more than the feature.

## Why this hurts with an AI editor specifically

AI agents are remarkably reluctant to look at adjacent files. They work with what's open and make confident changes from a partial picture. The FSD layout maximises exactly the cross-file lookups an agent won't perform:

- The checkout `ui` component's props are shaped by a type in `model`, the call lives in `api`, and the Stripe key or plan constants live in `config`. To safely edit the component, an agent has to open four siblings. It usually won't — it'll edit from what it sees and break something two files over.
- `index.ts` barrels make this worse, not better. They add an indirection hop: the agent reads `import { x } from '../model'`, lands on a re-export, and has to chase it again to find the real definition. More tokens, more hops, more chances to give up before reaching the thing it needs.

The skill's decision test is *"can this concern be understood in isolation?"* — not *"is this a separate concern?"* Slicing by technical layer (api/model/ui) almost guarantees each slice is *not* understandable alone, because a feature this contained is tightly coupled across those layers. You'd be splitting along the boundaries that survive worst.

## What I'd do instead

Start coarser. Organise by the three things the feature actually is, and let each file hold its own logic, types, and rendering together:

```
billing/
  PlanPicker.tsx        # component + its local types + presentation
  InvoicesList.tsx      # component + its local types
  checkout.ts           # the checkout call + its request/response types
  billing.ts            # shared types/constants, IF anything is genuinely shared
```

Each file stands on its own. An agent asked to "change the checkout flow" opens `checkout.ts` and has the whole picture. Asked to "tweak the plan picker UI," it opens one file and everything it needs is there.

A couple of refinements from the heuristics:

- **Reach for an abstraction before a folder.** If the checkout logic grows stateful (loading, error, redirect handling), a `useCheckout()` hook is worth far more than an `api/` folder. The component reads `useCheckout()` at the call site and knows enough to proceed without opening the implementation. That's a real interface that *reduces* context; a folder split just relocates code.
- **Raise your size threshold.** The "small files each in their own folder" instinct is calibrated for human scrolling. Agents handle cohesive files up to a few hundred lines fine. A 150-line `PlanPicker.tsx` that keeps its types and markup together beats three 50-line files that are meaningless apart. Split when a file passes ~300 lines or stops being one coherent concern — not by reflex.
- **Skip the barrels.** Direct imports give the agent a path straight to the definition. Add an `index.ts` only if/when something outside `billing/` consumes it and you want a deliberate public surface — and even then, one barrel at the feature root, not one per layer.

## The honest caveat

This isn't "FSD is bad." If your app already uses FSD everywhere, consistency has real value, and a layered billing feature that matches the rest of the codebase may be worth more than a locally-optimal one-off. FSD also earns its keep on large, genuinely complex features where the layers each hold substantial, independently-meaningful code. The point is that *this* feature isn't that — so don't pay the structural tax by default. Let billing grow into more structure if and when it actually gets complicated. It's much easier to split a coherent file later than to reassemble a feature scattered across five folders.

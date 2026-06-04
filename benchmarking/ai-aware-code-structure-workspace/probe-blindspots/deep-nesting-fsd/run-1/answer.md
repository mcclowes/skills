# Should billing/ use the full FSD layered folder structure?

Short answer: no, not as a default for a feature this small. The full `api/ model/ ui/ lib/ config/` split, each with its own little files and an `index.ts`, is over-engineered for a plan picker, a checkout call, and an invoices list — and it's actively working against you given that almost all your editing happens through Claude Code.

## Why the instinct misfires here

Feature-Sliced Design's layered slices are a real pattern, but they're a tax you pay for scale: many features, shared conventions across a big team, code you want to enforce strict dependency rules on. You'd be paying that tax up front on three small surfaces that don't need it yet.

The bigger issue is the AI-editing angle. The thing that makes layered FSD pleasant for humans — you intuitively glance at the sibling `model/` file while editing `ui/`, hold the shape of a type defined two folders over — is exactly the thing today's coding agents are bad at. Agents are strikingly reluctant to look at adjacent files. They work with what's open and make confident changes based on it. When a checkout flow is spread across `ui/CheckoutButton.tsx`, `model/checkout.ts`, `api/checkout.ts`, and `lib/`, and the agent is parked in one of them, it routinely lacks context that lives elsewhere — the shape of a request, a type, a returned object — and breaks things because it never opened the sibling.

So the deep folder tree doesn't just cost you ceremony. It scatters each feature across exactly the cross-file lookups the agent is most likely to skip. Every `index.ts` barrel adds another hop of indirection between the call site and the real code.

## The test to apply instead

For each piece, don't ask "is this a separate concern?" Ask: **can this be understood in isolation?**

- The **plan picker**, if it's mostly presentational (plans in, selection out), genuinely stands alone — that's a fine separate file. Pure props-to-output units are self-documenting and need almost no external context, so they're the *good* kind of split.
- The **checkout call** — UI, the state/effect orchestration around it, and the actual API call — is tightly coupled by nature. Understanding any one part means understanding the others. Splitting it across `ui/`, `model/`, and `api/` just creates three files that are each meaningless alone and triples the lookups the agent won't perform. Co-locate it.
- The **invoices list** — fetching plus rendering — same story. Keep the fetch and the render together unless the list view itself is cleanly presentational, in which case peel *only* the dumb presentational part out.

## What I'd scaffold instead

Start coarser than FSD suggests and let files grow while they stay coherent. Something like:

```
billing/
  PlanPicker.tsx        // presentational, stands alone
  Checkout.tsx          // UI + the orchestration it needs, together
  InvoicesList.tsx      // fetch + render co-located
  api.ts                // the actual HTTP calls (real network boundary)
  types.ts              // shared shapes, if there genuinely are cross-cutting ones
```

Flat, few files, each one self-sufficient. A cohesive 150-line `Checkout.tsx` that keeps its logic and rendering together is a *better* prompt for Claude Code than four 40-line files it has to stitch together in its head. Agents handle a few hundred lines fine; the human-era "split when it doesn't fit on screen" reflex is calibrated for scrolling, not for this.

The one boundary worth keeping is `api.ts`, because the network call is a real abstraction with a real interface, not just relocated code. That's the move to prefer in general: when a part earns its own name, reach for an **abstraction** (a `useCheckout()` hook, an `api.ts` module) rather than a folder. The agent reads `useCheckout()` at the call site and knows enough to proceed without opening the internals. A barrel `index.ts` does the opposite — it hides nothing and adds a hop.

## When to revisit

This isn't "FSD is wrong." It's wrong *for this size, today, with this toolchain*. Promote toward the layered structure when a slice actually earns it:

- a file pushes past ~300 lines or starts juggling several unrelated concerns,
- you've got enough billing surfaces that a shared `model/` or `lib/` would remove real duplication,
- or the team grows to where enforced dependency directions pay for themselves.

Let the structure grow into FSD when the feature does, rather than scaffolding the cathedral around three rooms.

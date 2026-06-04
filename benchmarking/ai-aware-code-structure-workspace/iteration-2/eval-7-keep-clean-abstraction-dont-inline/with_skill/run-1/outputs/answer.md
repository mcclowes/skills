# Don't inline it. Keep `calculatePrice.ts` as is.

Short version: this is the rare case where the human-readability, maintainability, *and* AI-readability arguments all point the same way — keep the file. The teammate's instinct ("Claude should see the whole flow in one place") is reasonable, but it's solving a problem that `calculatePrice.ts` doesn't actually have.

## Why this is a clean boundary, not an arbitrary split

The thing that makes a split bad for AI agents is when each resulting file is *meaningless without the other* — the agent lands in one file, can't understand it without opening a sibling it won't proactively open, and makes a confident-but-wrong change. That is the failure mode to design against.

`calculatePrice.ts` is the opposite of that. It's:

- **A pure function** — inputs in, outputs out, no side effects, no hidden state.
- **Fully typed on both ends** — the interface *is* the documentation. An agent editing `CheckoutSummary` reads `calculatePrice(input): Price` at the call site and knows everything it needs to proceed without opening the file.
- **Understandable in isolation** — an agent editing the pricing logic can work entirely within `calculatePrice.ts` and its test, with no need to understand React, checkout state, or rendering.

That's a *real abstraction*, not just relocated code. It has an interface, it hides its implementation, and it reduces the context needed on both sides of the boundary. That's the single most valuable property you can have in an AI-assisted codebase — and it's exactly what inlining would destroy.

## What inlining actually costs

1. **It deletes the interface.** Right now the type signature tells the agent (and humans) the contract. Inline 120 lines of pricing math into a component and that contract dissolves into the component body. Future edits to checkout rendering now happen *next to* pricing logic the agent has to read past, and edits to pricing happen tangled in JSX/state.

2. **The test gets orphaned.** `calculatePrice.test.ts` targets a clean function boundary. Inline the function and either the test breaks or you're now testing pricing through a React component — slower, flakier, and a strictly worse signal. You'd be trading a fast, focused unit test for component-level testing of pure math.

3. **It breaks 6 call sites or duplicates the logic.** Six imports means six places that rely on this contract. Inlining either forces them all to reach into a component (a worse dependency direction — UI shouldn't be the home of shared domain logic) or, more likely, leads to the logic being copy-pasted. Now pricing rules live in N places and an agent fixing a bug in one won't know about the others. That's a far nastier "AI can't see everything" problem than the one the teammate is trying to solve.

4. **It makes `CheckoutSummary` worse as a prompt.** The component would balloon by ~120 lines of dense, non-rendering logic. A focused component is a *better* context window for an agent than a 300-line file doing everything. Inlining lowers the signal-to-noise ratio of the exact file the teammate cares most about editing.

## The teammate's real concern is legitimate — solve it differently

The worry is that an agent editing checkout won't "see" the pricing flow. Two cheap fixes that keep the abstraction:

- **Make the seam obvious at the call site.** A well-named import (`import { calculatePrice } from '../pricing/calculatePrice'`) plus the typed signature already tells the agent what pricing does and where it lives. If the types are expressive, the agent rarely needs the body.
- **Leave a one-line breadcrumb** in `CheckoutSummary` if discoverability genuinely bites — e.g. a comment noting that pricing rules live in `pricing/calculatePrice.ts`. That's far cheaper than merging two concerns.

In practice, agents follow a single explicit import far more reliably than they reconstruct logic buried in a 300-line component. A clean named function isn't *harder* for the agent — it's easier, because it can trust the interface instead of re-reading the implementation every time.

## Where the teammate would be right

This advice flips if the function weren't actually self-contained — if "calculatePrice" secretly reached into checkout state, depended on render-time values, or only made sense alongside the component. Then you'd have a fake boundary: two files meaningless apart, and merging them would genuinely help. But a pure, typed, tested, 6x-reused function is the textbook case of a boundary worth keeping.

## Recommendation

Keep `pricing/calculatePrice.ts` and its test exactly where they are. If discoverability is the real concern, address it with a clear import and maybe a one-line pointer comment — not by collapsing a clean, reused, well-tested abstraction into a UI component. Inlining here trades a strong asset for a weak one.

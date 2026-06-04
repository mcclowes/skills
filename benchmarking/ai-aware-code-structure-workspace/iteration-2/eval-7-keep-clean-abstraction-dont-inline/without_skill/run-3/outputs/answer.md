# Don't inline it

Short answer: no, keep `calculatePrice.ts` as a standalone, tested, pure function. Inlining it would trade away real, durable structure for a perceived AI-context benefit that doesn't actually hold up — and the AI-context argument is the *weakest* part of your teammate's case, not the strongest.

## Why the "so Claude sees the whole flow" reasoning is backwards

The intuition is that a coding agent does better when everything lives in one file. In practice the opposite is closer to true, for a few concrete reasons:

- **Agents follow imports just fine.** When Claude (or any competent assistant) is editing `CheckoutSummary` and needs to understand pricing, it can open `calculatePrice.ts` in one step. A single named import is a *signpost*, not a barrier — it tells the agent exactly where pricing lives, with a typed signature describing the contract. That's higher-signal than 120 lines of arithmetic buried inside a component.
- **Smaller, single-purpose files are easier for an agent to edit safely.** A pure function with typed inputs/outputs and its own test file is the ideal editing target: the agent can change it, run `calculatePrice.test.ts`, and get immediate, isolated feedback. Inlined into a component, the same edit now sits next to JSX, hooks, state, and effects — more surrounding context to mislead the model, a bigger blast radius, and no fast unit test to confirm the change.
- **"One place" only helps if that place is the *right* size.** Co-location helps when things genuinely change together. Pricing logic and checkout *rendering* don't: one is deterministic computation, the other is React lifecycle and layout. Merging them doesn't give the agent "the whole flow," it gives the agent two unrelated concerns tangled together.

So even on its own terms — optimizing for AI assistants — inlining is the wrong call.

## The non-AI reasons are decisive on their own

Set the AI argument aside and the case is still clear:

1. **It's imported by 6 call sites.** Inlining into `CheckoutSummary` means either (a) those 6 sites now import pricing logic *from a React component* — a terrible dependency direction, pulling component/UI baggage into non-UI code — or (b) you duplicate the logic 6 ways. Both are strictly worse than one shared module. This point alone settles it.
2. **It's pure and fully typed.** This is the easiest possible thing to test, reason about, and reuse. That's a property worth protecting, not dissolving.
3. **You'd lose the dedicated test.** `calculatePrice.test.ts` tests pricing in isolation. Once the logic lives inside a component, you can only exercise it through component rendering — slower, flakier, and far harder to cover edge cases (rounding, discounts, tax, currency). Pricing is exactly the kind of money-touching logic you want unit-tested directly.
4. **120 lines of pricing math is a lot to bury in a UI component.** It will make `CheckoutSummary` meaningfully harder to read for humans *and* agents.

## The kernel of truth worth addressing

Your teammate is reacting to a real feeling: "when I'm editing checkout, the pricing logic feels far away." That's a discoverability concern, and it's legitimate. The fix is to make the boundary *more* navigable, not to delete it:

- Keep the function where it is, but make sure the import and call site read clearly (e.g. `const price = calculatePrice(cart, options)` with a self-describing typed result).
- Add a one-line doc comment or a `// pricing logic: ./pricing/calculatePrice.ts` pointer at the call site if people keep losing it.
- If `pricing/` has grown several related modules, an `index.ts` barrel or a short README in that folder gives both humans and agents an obvious entry point.
- Make sure the types live with the function so the contract travels with the import.

## Recommendation

Keep `calculatePrice.ts` as a separate pure, typed, tested module. Decline the inline. If the goal is genuinely "help Claude work on checkout," the higher-leverage moves are clear module boundaries, descriptive names, and fast isolated tests — all of which the current structure already gives you and inlining would destroy. The clean abstraction is the AI-friendly choice here, not the obstacle.

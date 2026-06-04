# Don't inline it

No, keep `calculatePrice.ts` as it is. Inlining would make the codebase worse for AI assistants, not better — your teammate has the right instinct (give the agent the whole picture) but the wrong fix.

## Why this is exactly the case where you keep the file

`calculatePrice` is the textbook example of code that should stay separate, even in an AI-heavy workflow:

- **It's a real abstraction, not just a relocated blob.** It has a typed interface — inputs in, outputs out — and it hides its implementation. When an agent is editing `CheckoutSummary` and sees `calculatePrice(cart, ...)`, the call site plus the types tell it everything it needs to proceed. It doesn't have to read the 120 lines of internals to work on the checkout flow. That's the goal: an abstraction *reduces* the context an agent needs, whereas inlining just dumps 120 more lines into the file it's already working in.
- **It can be understood in isolation.** Pure function, fully typed, no side effects. This is the strongest possible candidate for its own file — the agent can work on pricing with almost no external context, and the file is self-documenting.
- **It has its own tests.** `calculatePrice.test.ts` only makes sense next to a standalone, importable function. Inlining either orphans those tests or forces you to test pricing through the React component, which is slower, flakier, and much harder for an agent to reason about.
- **6 call sites.** This is decisive. Inlining into `CheckoutSummary` means either duplicating the logic 6 times or having the other 5 sites import pricing logic *out of a React component* — a genuinely bad dependency direction. One pure module that six places import is the clean shape.

## The teammate's actual concern is valid — but inlining doesn't solve it

The worry is real: agents are reluctant to look at adjacent files, so "the pricing logic lives one import away" can mean the agent edits checkout without understanding pricing. But notice what's actually true here:

- The agent **doesn't need** to open `calculatePrice.ts` to work on checkout. The typed signature is the contract. That's the whole point of a clean abstraction — the call site is enough.
- If the agent **does** need to change pricing logic, it should be editing `calculatePrice.ts` (and its test) directly — a tightly focused 120-line file with high signal-to-noise, which is a far better prompt than a 240-line `CheckoutSummary` mixing rendering, state, and pricing math.

Inlining would trade a clean interface for a busier, multi-concern component and would *worsen* signal-to-noise in the exact file the agent edits most. The "co-locate so the agent sees everything" heuristic is for code that's **meaningless apart** — logic and rendering that each need the other to make sense. Pricing isn't that. It stands fully on its own.

## Better ways to get "the agent sees the whole flow"

If the goal is helping an agent understand how checkout and pricing connect, do it without merging:

- Keep the import explicit and the types shared, so the signature at the call site carries the contract.
- Add a short doc comment at the top of `CheckoutSummary` (or a one-line pointer) noting that pricing lives in `pricing/calculatePrice.ts` — a cheap breadcrumb if you want to nudge the agent to look.
- If anything, the move is *up*, not in: a `useCheckout()`-style hook wrapping the orchestration, with `calculatePrice` staying pure underneath.

## Bottom line

Keep the file. It's a pure, typed, tested, reused abstraction — the single clearest "don't merge" case there is. Inlining would duplicate or misplace logic across 6 call sites, orphan a clean test, and lower signal-to-noise in the component the agent touches most. The interface is the context the agent needs; the 120 lines of implementation are noise it's better off not loading.

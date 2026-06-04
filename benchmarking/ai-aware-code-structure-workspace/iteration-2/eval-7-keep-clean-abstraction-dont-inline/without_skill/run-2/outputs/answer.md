# Don't inline it. Keep `calculatePrice.ts` as is.

Short answer: no, inlining is the wrong move here, and the reasoning behind it is based on a misunderstanding of how AI assistants actually work in a codebase.

## Why this is a strong "keep it" case

You've described almost a textbook example of a function that *should* be its own module:

- **It's pure.** No side effects, no hidden state. Easy to reason about and test in isolation.
- **It's fully typed at the boundary.** Inputs and outputs are explicit contracts.
- **It has its own tests.** `calculatePrice.test.ts` can hammer the pricing logic directly without mounting a checkout component.
- **It has 6 call sites.** This is the killer detail. Inlining a function used in 6 places means either duplicating ~120 lines six times, or leaving it in CheckoutSummary and having the other 5 call sites import pricing logic *out of a React component*. Both outcomes are clearly worse.

That last point alone settles it. You can't actually "inline" something with 6 consumers without either creating duplication or making `CheckoutSummary` a weird de-facto utility module that five unrelated places reach into.

## The AI argument is backwards

The teammate's premise is "Claude sees the whole pricing flow in one place when editing checkout." But a separate, well-named file is *better* for AI assistants, not worse:

1. **Tooling finds it instantly.** When an agent edits checkout, `calculatePrice(...)` is right there in the code. Go-to-definition, grep, and the import statement all point straight to the file. Reading one extra file with an obvious name is cheap. There's no meaningful "context cost" to a 120-line file that the model opens on demand.

2. **A focused file is a tighter context window.** A 120-line pure function with clear types is the *ideal* thing to hand an AI when the task is "change how pricing works." A 400-line component that mixes pricing math, JSX, state, and effects is harder for a model to edit safely. Inlining makes the high-stakes logic harder to isolate, not easier.

3. **The test file is the real safety net.** When an AI edits pricing, `calculatePrice.test.ts` is what catches mistakes. Inlining typically orphans or dilutes those tests into component tests that need rendering, mocks, and setup. You'd be trading fast, precise unit tests for slow, brittle ones — and AI-generated changes are exactly when you most want a fast, precise test to fail loudly.

4. **Blast radius matters more with AI in the loop.** Agents make confident, sweeping edits. A pure function with one responsibility and six callers gives you a small, well-defined surface to review. Fold it into a component and an edit to "fix a checkout layout bug" can now silently change pricing for five other call sites.

The actual concern — "will the AI understand the pricing flow?" — is solved by good naming, types, and a short doc comment, not by physical co-location. If you want to help the assistant, add a one-line comment at the import site or a brief JSDoc on `calculatePrice` describing the flow. That's the cheap, correct fix.

## When inlining *would* be reasonable (not your case)

To be fair to the teammate, inlining isn't always wrong. It's defensible when:

- The function has exactly **one** caller and no realistic prospect of more.
- It's trivial (a few lines), with no independent test worth keeping.
- The indirection genuinely obscures rather than clarifies — a thin pass-through wrapper that adds nothing.

None of these hold here. You have 6 callers, 120 lines of real logic, and a dedicated test suite. This is the opposite of a needless abstraction; it's a clean seam that's earning its keep.

## Recommendation

Keep `pricing/calculatePrice.ts` and its test exactly where they are. If discoverability is the real worry, address it directly:

- Make sure the function and its types have clear, intention-revealing names.
- Add a short JSDoc summarizing the pricing flow and the order of operations.
- Optionally, leave a one-line comment at the CheckoutSummary call site pointing to it.

That gives the AI (and humans) the "whole flow in one place" understanding the teammate wants, without sacrificing testability, reuse, or a small review surface. Inlining would cost you all three to solve a problem that go-to-definition already solves for free.

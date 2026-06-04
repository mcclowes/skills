# Don't inline it

Short answer: no, keep `calculatePrice.ts` as a separate module. Inlining it would trade away real, durable benefits for a perceived AI convenience that doesn't actually hold up.

## Why the current structure is right

You have a textbook-good unit here:

- **Pure function.** No side effects, deterministic. This is the easiest possible thing to reason about, test, and reuse.
- **Fully typed inputs and outputs.** The signature *is* the contract. Anyone — human or AI — can understand what goes in and what comes out without reading the body.
- **120 lines.** That's a meaningful amount of logic. Inlined into a React component, it bloats the component and tangles pricing rules with rendering concerns.
- **Its own test file.** Co-located tests on a pure function are gold. You can change pricing logic and get fast, focused feedback without mounting a component or mocking checkout state.
- **6 call sites.** This is the decisive point. The function is shared. Inlining it into `CheckoutSummary` either (a) duplicates the logic across 6 places, or (b) forces the other 5 call sites to import pricing logic *from a UI component*, which is a worse dependency direction than what you have now.

That last point alone should settle it. The moment something has 6 consumers, it's infrastructure, not a local helper. You can't inline a shared dependency into one of its consumers without harming the other five.

## The AI argument doesn't survive scrutiny

The teammate's reasoning is "so Claude sees the whole pricing flow in one place when editing checkout." A few problems with that:

1. **AI assistants follow imports.** A typed import like `import { calculatePrice } from '../pricing/calculatePrice'` is a clear, greppable signpost. When an agent edits checkout and needs the pricing logic, it opens that file — the same way it would scroll to a different region of a giant component. Locating it is trivial; the filename literally says what it does.

2. **Smaller, well-named files are *easier* for AI, not harder.** A 120-line pure function with a clear signature is a clean, self-contained context window. A `CheckoutSummary` that now also contains all pricing logic is a larger, noisier file where an agent editing the *layout* has to wade through pricing math it doesn't care about — and risks touching it by accident.

3. **The test file is an AI superpower, and inlining weakens it.** When an agent changes pricing logic, `calculatePrice.test.ts` gives it an immediate, isolated verification loop. Fold the logic into a component and those tests get harder to keep tight; the feedback signal degrades exactly when you most want it.

4. **"One place" is a context-window heuristic from a bygone era.** Modern agents navigate multi-file codebases routinely. Optimizing your architecture so a model never has to open a second file is optimizing for the wrong constraint — and you'd be paying for it with every human who reads the code too.

## The real risks of inlining

- **Duplication or drift** across the 6 call sites, or an inverted dependency (logic imported from a UI component).
- **Coupling pricing correctness to React.** Pricing bugs are expensive. You want that logic testable in isolation, framework-free, forever.
- **A fatter component** that mixes "what to charge" with "how to render the summary" — two concerns with different reasons to change.
- **Harder reviews.** A pricing change buried in a component diff is easier to miss than a focused diff in `calculatePrice.ts`.

## If the real problem is discoverability

The teammate's instinct usually comes from a real friction: "I didn't realize the pricing lived over there." Solve *that* directly instead of collapsing the boundary:

- Add a one-line comment at the call site in `CheckoutSummary` pointing to the module, or rely on the already-clear import path.
- Keep the module name and exported function name descriptive (you already do).
- If pricing is several related files, group them under a `pricing/` directory with a small `index.ts` barrel so the whole domain is one obvious place — *separate from* checkout UI, not merged into it.

## Bottom line

Keep `calculatePrice.ts` separate. A pure, typed, tested, 6-times-reused function is one of the highest-leverage abstractions you can have, and it serves AI assistants *better* than an inlined version, not worse. The "see it all in one place" benefit is illusory — agents follow imports fine — while the costs (duplication, inverted dependencies, weakened tests, a bloated component) are concrete and permanent. Push back on this one.

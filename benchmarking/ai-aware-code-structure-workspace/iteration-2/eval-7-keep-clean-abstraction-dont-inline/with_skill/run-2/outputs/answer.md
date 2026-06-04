# Don't inline it. Keep `calculatePrice.ts` as is.

Short version: your teammate's instinct (give the agent the whole flow in one place) is right in general but points the wrong way here. `calculatePrice` is already the thing you'd *want* to exist for AI-assisted work. Inlining it would make checkout worse for both humans and Claude.

## Why it stays

`calculatePrice` is a **real abstraction**, not a file split for tidiness. It has a typed interface — inputs and outputs — and it hides its implementation behind a name. That's the single most valuable shape for an AI agent. When Claude is editing `CheckoutSummary`, it reads:

```ts
const price = calculatePrice(inputs)
```

and it knows enough to proceed. It doesn't need the 120 lines of logic in context to reason about the checkout flow. The typed signature *is* the summary of the pricing flow. That's strictly better than inlining, which would relocate 120 lines into the component and force the agent to hold all of it in context every time it touches anything in checkout — including changes that have nothing to do with pricing.

The relevant rule of thumb: prefer an abstraction over file structure, and an abstraction over inlining. A well-named function reduces the context needed to work with the code. Inlining only increases it.

## The teammate's reasoning, addressed directly

"So Claude sees the whole pricing flow in one place" — it already does, better than the inlined version would. The whole pricing flow lives in exactly one place today: `calculatePrice.ts`. If Claude needs the internals, that one file is self-contained, pure, and has its own tests right beside it — about as easy to open and fully understand as a file gets. If Claude *doesn't* need the internals (the common case when editing layout, copy, or wiring in `CheckoutSummary`), it pays nothing for them.

The thing AI agents are bad at — reluctant to chase context across several files where each is meaningless alone — does not apply here. This isn't a "dumb render file whose props are shaped by a sibling." It's a pure function with a typed boundary. The boundary is exactly where it should be: each side stands on its own.

## The costs of inlining

- **You'd lose `calculatePrice.test.ts`'s reason to exist.** A pure function is trivially testable in isolation. Inlined into a component, that logic becomes reachable only through component rendering, so the focused unit tests get harder to keep or get deleted. You'd be trading a fast, precise test surface for a worse one.
- **Five other call sites.** It's imported in 6 places. Inlining into `CheckoutSummary` either duplicates the logic across those call sites or forces them to import it *from* a component — both are worse than importing a pure function from a `pricing/` module. Duplicated pricing logic is exactly the kind of thing that drifts and causes real bugs.
- **`CheckoutSummary` gets bigger and noisier.** Adding 120 lines of pricing math to a component lowers its signal-to-noise. When Claude edits the component, that math is now context it has to wade through for unrelated changes. Focused files make better prompts.
- **Purity gets diluted.** Right now the function is pure: inputs in, outputs out, no side effects, easy to reason about and verify. Drop it into a stateful component and that clean property is easy to erode over time.

## When inlining *would* be right (and why this isn't it)

Inlining is the correct move when a "split" left you with files that only make sense together — e.g. a presentational fragment whose props are shaped by a sibling the agent won't open. There, merging back gives the agent a complete picture. That's the opposite of your situation: `calculatePrice` is complete on its own and shared by six callers.

## Recommendation

Keep `pricing/calculatePrice.ts` and its test exactly where they are. If the real worry is discoverability — Claude not realising pricing lives there — the fix is a pointer, not a merge:

- A one-line comment at the pricing call site in `CheckoutSummary` (e.g. `// pricing logic lives in pricing/calculatePrice.ts`), or
- A short note in the checkout area's `CLAUDE.md` / README saying pricing is computed by `pricing/calculatePrice`.

That gives the agent the breadcrumb your teammate wants without paying the context, testing, and duplication costs of inlining. Net: this is a clean abstraction doing its job — leave it.

# Should you split CheckoutForm.tsx?

Short answer: not yet, and probably not into the three-file shape you're describing. At 180 lines holding state, one effect, a submit handler, and JSX, this is a perfectly healthy single file. The smart/dumb/styles split is a habit worth re-examining now that most of your editing runs through Claude Code.

## Why the classic three-way split doesn't earn its keep here

The container/presentational pattern was popularized in a world where:

- You manually navigated between files in an editor, so co-location mattered less than "separation of concerns" as a mental model.
- Reuse of the dumb component across multiple containers was common.
- Class components made it genuinely awkward to mix data and rendering.

None of those strongly apply to a single checkout form edited by an agent:

- **You're not reusing the presentational layer.** A CheckoutForm's JSX is bound to its specific fields and submit logic. Splitting it produces a "dumb" component with a 15-prop interface that exists only to serve one parent. That prop interface is pure overhead — every change to the form means editing two files and the contract between them.
- **The split hurts the agent more than it helps.** When Claude Code edits this component, having state, effect, handler, and JSX in one file means one Read gives it the full picture. Split across three files, it has to open all three, reconstruct the prop contract in its head, and keep them in sync. You increase the surface area for "edited the container but forgot to thread the new prop through." Co-located code is easier for an LLM to reason about and change correctly, not harder.
- **"Separation of concerns" via file boundaries is the weakest form of the principle.** You can separate concerns *within* a file — clear sections, well-named functions, a typed state shape — without paying the cross-file coordination tax.

## What I'd actually do

Leave it as one file, but tidy it internally so it reads top-to-bottom cleanly:

1. **Lift genuinely reusable, testable logic into hooks or plain functions** — but only where there's a real seam:
   - The saved-cards fetch in the `useEffect` is a good candidate for a `useSavedCards()` hook. It has a clear input/output contract (loading, error, cards), it's independently testable, and you'll likely want it elsewhere (account page, one-click checkout). This is a split that *earns* its keep because it isolates async/network behavior you'll want to mock in tests.
   - The submit handler that calls the payments API can become a small `submitPayment(payload)` function in a `payments` module if that call isn't already centralized. Keep the *orchestration* (validate → call → handle result → set UI state) in the component; move only the raw API call out.

2. **Keep state, JSX, and orchestration together.** This is the part that changes as one unit. Don't separate it.

3. **Styles: follow your existing convention.** If the codebase uses SCSS modules (per your usual stack), a `CheckoutForm.module.scss` next to the component is fine and idiomatic — that's not really a "concern split," it's just where CSS lives. Don't make a decision about it on architectural grounds; match the repo.

So the likely end state is two or three files, but along *capability* lines, not *layer* lines:

```
CheckoutForm.tsx          // state, effect orchestration, handler orchestration, JSX
useSavedCards.ts          // the fetch effect, extracted because it's reusable + testable
CheckoutForm.module.scss  // styles, per house convention
payments.ts               // if the API call isn't already centralized
```

## When you *would* split the component itself

Revisit this if the file crosses roughly 300–400 lines, or if a clear sub-region emerges that has its own state and could be reused — e.g. a `SavedCardSelector` that manages its own selection state and shows up on more than one screen. At that point the boundary is real and the extracted piece stands on its own. Splitting before that just to honor a pattern creates two coupled files where one cohesive file did the job.

## Bottom line

Don't do the smart/dumb/styles split — it adds a prop-contract tax that buys you nothing here and makes agent edits more error-prone. Instead, extract `useSavedCards` (reusable, testable network logic) and centralize the payments call, then keep state, orchestration, and JSX co-located in `CheckoutForm.tsx`. Split along capabilities you'll reuse or test in isolation, not along architectural layers.

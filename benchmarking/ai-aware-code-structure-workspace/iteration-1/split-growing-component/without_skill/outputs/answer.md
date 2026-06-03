Short answer: at 180 lines, I wouldn't reflexively split it three ways. The container/presentational split is a habit worth questioning here, especially given how you work now.

Let me challenge the instinct first, then give you a split that's actually worth doing if the file keeps growing.

## Why the classic three-way split is weaker than it used to be

The container/dumb/styles pattern solved real problems in 2016-2018: class components couldn't share stateful logic, so you hoisted state into a container and passed it down. Hooks killed most of that reason. You can now extract stateful logic without extracting a component.

A few specific pushbacks:

1. **180 lines is not large.** A component holding form state, one `useEffect`, a submit handler, and JSX is a normal, readable size. Splitting it now mostly moves code around rather than reducing complexity. You'd trade one 180-line file for three files plus the prop-passing boilerplate that wires them together. The total cognitive load often goes *up*, not down.

2. **The presentational/container split tends to create a fake seam.** You end up with a "dumb" component whose props interface is just a mirror of the container's internals: `savedCards`, `onSubmit`, `isLoading`, `error`, `selectedCard`, `onSelectCard`... When the presentational component's prop list is basically "every piece of state the container has," you haven't decoupled anything. You've added an indirection layer and a place for the two files to drift out of sync.

3. **Styles-in-a-separate-file is orthogonal** to the component split and you can do it any time independently. If you're on CSS/SCSS modules that's already your default; if you're on a CSS-in-JS or Tailwind setup, a separate styles file may not even make sense. Don't bundle that decision into the component-splitting decision.

## The split that *is* worth doing

Instead of splitting by "smart vs dumb component," split by **concern that has a reason to live on its own**. The strongest candidate in what you described is the data + API logic, extracted as **hooks**, not components:

```
CheckoutForm.tsx          // the component: state wiring + JSX
useSavedCards.ts          // the useEffect that fetches saved cards
useCheckoutSubmit.ts      // the submit handler + payments API call
```

Why this beats container/presentational:

- **`useSavedCards`** owns the fetch, loading state, error state, and cleanup/cancellation. That's genuinely reusable and genuinely testable in isolation (you can test the fetch logic without rendering anything). It also gets the async lifecycle bug-bait out of the component body.
- **`useCheckoutSubmit`** owns the call to your payments API, the in-flight state, and error mapping. Payment submission is exactly the kind of logic you want to unit-test hard and possibly reuse (retry flows, a one-click variant, etc.).
- **`CheckoutForm.tsx`** stays a single component but shrinks to: local form field state + `const { cards, loading } = useSavedCards()` + `const { submit, submitting, error } = useCheckoutSubmit()` + JSX. Reads top-to-bottom, no prop-drilling between two halves of the same screen.

This is the modern version of "separate the smart part from the rendering." The smart part becomes hooks, and the rendering stays where it is. You get the testability and reuse benefits without the mirrored-props indirection.

If the JSX itself gets unwieldy later (say the saved-cards list grows its own logic), *then* pull out a child component like `<SavedCardSelector />` — but extract it because that subtree is a real, self-contained unit, not because of a "dumb component" rule.

## The Claude Code angle, since you raised it

You mentioned most of your editing happens through Claude Code now, and that genuinely changes the calculus a bit — though maybe not in the direction you'd expect:

- **More files is not free.** Every split means the model (and you) may need to open and reconcile more files to make one change. A change that touches the prop contract between a container and a presentational component is now a two-file edit that has to stay in sync. A single cohesive file is often easier to edit correctly in one pass.
- **What *does* help the model:** clear boundaries with real interfaces. A hook with a typed return value (`{ cards, loading, error }`) is a crisp contract the model can rely on without reading the implementation. That's the kind of split that pays off — strong types at the seam, not just physical file separation.
- **Net:** don't split *for* the tooling. Split where there's a genuine reason (testability, reuse, isolating async/lifecycle complexity), keep strong TypeScript types at every boundary, and keep cohesive things in one file. Both you and Claude Code edit cohesive, well-typed code more reliably than scattered code with implicit contracts.

## My recommendation

1. **Don't do the three-way container/dumb/styles split.** It's solving a 2017 problem.
2. **Do extract the two pieces of logic that have a life of their own** — `useSavedCards` (the fetch + its effect) and `useCheckoutSubmit` (the payments call) — as hooks with explicit typed return shapes. Write tests against those hooks; that's where your TDD effort gives the most return, since payments and async fetching are the risky bits.
3. **Leave the form state and JSX in `CheckoutForm.tsx`.** Touch the styles file only if your styling approach already wants one; treat it as a separate, independent decision.
4. **Re-evaluate splitting the JSX only if a subtree grows its own logic**, and extract by cohesion, not by a smart/dumb rule.

If you want, point Claude Code at the file and ask it to extract `useSavedCards` and `useCheckoutSubmit` with typed returns and a couple of tests for each — that's a clean, low-risk first move, and you can stop there and see if it actually feels better before doing anything more.

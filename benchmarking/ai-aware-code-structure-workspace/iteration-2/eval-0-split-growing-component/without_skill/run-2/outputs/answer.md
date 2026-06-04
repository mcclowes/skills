# Should you split CheckoutForm.tsx? Probably not yet.

Short version: at ~180 lines, I'd leave it as one file. The smart/dumb/styles split you're describing is a pattern from a specific era (HOCs, class components, Redux `connect`) that solved problems you mostly don't have anymore — and it actively works against an AI-assisted workflow.

## Why the old instinct doesn't pay off here

The container/presentational split earned its keep when:

- You wanted to reuse the dumb component with different data sources.
- You were unit-testing the presentational layer in isolation by passing props.
- `connect()` forced a wrapper component anyway, so you got the boundary "for free."

None of those apply to a checkout form. It's used in exactly one place, its state and its markup are tightly coupled (the form fields *are* the state), and the realistic test for it is "render it, fill it in, submit, assert the API was called" — which is an integration test against the whole thing, not a props-in/JSX-out snapshot.

So the split would buy you a boundary you don't need, at the cost of three files that have to be opened and cross-referenced every time you touch the feature.

## Why this matters more now that you edit via Claude Code

This is the part I'd weight most heavily given how you work.

When the whole feature lives in one file, an agent reads it in a single pass and has complete context: the state shape, the effect that loads cards, the submit handler, and the JSX that wires them together. A change like "show a spinner on the saved-cards dropdown while it loads" is one coherent edit in one place.

Split it three ways and every non-trivial change becomes a multi-file hop: the agent edits the container, then has to thread a new prop through the presentational component's interface, then maybe touch styles. More files to locate, a prop-drilling contract to keep in sync, and more surface area to get subtly wrong. You pay a real token and accuracy tax for a separation that isn't earning anything. **Cohesion beats premature separation** — keep things that change together in the same file.

## What I'd actually do

Keep it as one component file. Extract only along seams where the logic is genuinely independent and reusable, not along the arbitrary "smart vs. dumb" line:

1. **Pull the data + side effects into a hook.** `useSavedCards()` (the `useEffect` + fetch + loading/error state) and possibly `useCheckoutSubmit()` (the payments API call + submission state). This is the split that actually pays off: it's testable on its own, it's reusable, and it cleanly separates "talk to the network" from "render the form." It also keeps the component body readable — the JSX stops being interleaved with fetch plumbing.

2. **Leave the form state and JSX together** in `CheckoutForm.tsx`. They're cohesive; the markup is the view of that state. One file.

3. **Styles: follow your project convention, but don't create a file for the split's sake.** If you're already on SCSS modules everywhere, a `CheckoutForm.module.scss` is fine and idiomatic — that's a real co-located pairing, not the old "styles file because the pattern said so." If you're using Tailwind/CSS-in-JS, don't invent a separate styles file just to honor the three-file shape.

That likely leaves you with:

```
CheckoutForm.tsx          // form state + JSX, imports the hooks
useSavedCards.ts          // fetch + loading/error
useCheckoutSubmit.ts      // payments API call + submission state
CheckoutForm.module.scss  // only if SCSS modules is your house style
```

## When to revisit

Split further when the file is actually telling you to, not on a line count:

- It crosses ~300–400 lines **and** you can point at two distinct responsibilities that change for different reasons.
- A second screen needs to reuse the form's markup with a different data source (then, and only then, the presentational extraction earns its keep).
- The submit handler grows real branching logic (multiple payment methods, 3DS, retries) — that's a sign `useCheckoutSubmit` wants to become its own well-tested module.

Line count is a smell, not a rule. 180 lines of cohesive form code is fine. 180 lines doing four unrelated things would not be. Yours sounds like the former.

## Bottom line

Don't do the smart/dumb/styles split — it's solving yesterday's problem and it makes every future edit (yours or the agent's) more expensive. Extract the network logic into hooks, keep state and JSX together, and let the file grow until it gives you a concrete reason to divide it.

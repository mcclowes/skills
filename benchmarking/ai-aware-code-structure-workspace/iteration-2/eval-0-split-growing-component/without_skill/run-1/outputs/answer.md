# Should you split CheckoutForm.tsx?

Short answer: not yet, and probably not into the three-file container/presentational/styles shape you're reaching for out of habit. At ~180 lines with one form's worth of state, one effect, one submit handler, and its JSX, this file is still small and cohesive. The instinct to split is muscle memory from an era where the constraints were different. Let me make the case and then give you the split that's actually worth doing.

## Why the old three-way split doesn't earn its keep here

The smart/dumb (container/presentational) pattern solved real problems around 2016-2019: class components couldn't easily share logic, and the split let you reuse a presentational component with different data sources and test rendering in isolation. Hooks killed most of that rationale. Logic reuse is now a custom hook, not a wrapper component.

For a 180-line component, splitting into three files mostly buys you costs:

- **Prop-drilling boilerplate.** A dumb `CheckoutFormView` needs every piece of state, every handler, and every error string threaded through its props interface. You'll write and maintain a 15-field props type that exists only to ferry data across a file boundary you invented. When you add a field to the form, you now edit it in three places.
- **Indirection without payoff.** The presentational component has exactly one caller. A component with one consumer isn't reusable, it's just relocated. Anyone reading the code (you, a teammate, or Claude) now has to hold two files in their head to understand one form.
- **Worse, not better, for Claude Code.** This is the part your habit hasn't caught up to. When you ask Claude to "add a coupon field" or "handle the declined-card error," it works best when the state, the handler, and the JSX that consume each other sit in one buffer. A tightly cohesive single file means one read, one edit, full context. The three-file split forces it to open the container, the view, the props type, and the styles, reconcile them, and edit across all of them — more places to get the wiring subtly wrong, more tokens spent rebuilding context you already had for free. Locality of behaviour is the thing that makes an AI editor reliable, and the three-way split actively destroys it.

## What's actually worth extracting

There's one real seam in your description, and it's not rendering vs. logic. It's **the data/IO boundary**. Two things in this file talk to the outside world and have their own failure modes, retry concerns, and types:

1. The `useEffect` that fetches saved cards.
2. The submit handler that calls the payments API.

Those are the parts most likely to grow (loading states, error handling, retries, optimistic updates) and the parts you'll want to test without rendering a form. Pull each into a custom hook:

- `useSavedCards()` — owns the fetch, the loading/error state, returns `{ cards, isLoading, error }`. Replaces the bare `useEffect`.
- `useCheckoutSubmit()` (or a thin `submitPayment()` API function if there's no React state involved) — owns the call to the payments API, its in-flight and error state.

That leaves `CheckoutForm.tsx` holding form state and JSX — which belong together, because the JSX is what reads and writes that state. The component reads as a clear, linear story: pull saved cards from a hook, hold form state locally, render, submit through a hook.

This is a split along **what changes together and what fails together**, not along the cosmetic logic/markup line.

## On the styles file

Keep your existing convention. If the rest of the codebase uses SCSS modules (`CheckoutForm.module.scss`), a co-located styles file is fine and standard — that's a different axis from the component split and doesn't carry the prop-drilling tax. Just don't create it as a ceremonial third leg of a pattern; create it because you have styles. If it's a handful of classes, inline/utility classes are also fine.

## Concrete recommendation

1. **Don't** do container/presentational.
2. Extract `useSavedCards()` into its own file (e.g. `useSavedCards.ts`), with a colocated test.
3. Extract the payments call into `useCheckoutSubmit()` or a plain `submitPayment()` function, with a test.
4. Leave form state + JSX together in `CheckoutForm.tsx`.
5. Keep styles in whatever your project already uses.

You'll end up with roughly the same number of files you were going to create, but split along a boundary that pays you back: the IO logic is independently testable, the component stays readable top-to-bottom, and Claude Code can edit the form without juggling a props contract across files.

## When to revisit

Reconsider further splitting when concrete pressure shows up, not on a line count:

- The file pushes past ~300-400 lines and has clearly distinct sections (e.g. a multi-step wizard).
- A genuine second consumer appears for part of the markup, making a real shared subcomponent worthwhile.
- The JSX itself grows a self-contained chunk with its own local state (e.g. a saved-card picker with its own selection logic) — extract *that* as a component, by feature, rather than slicing the whole thing into smart/dumb halves.

Bottom line: split by IO boundary into hooks, not by render/logic into a container. It's better separation of concerns by the definition that matters — things that change and fail together stay together — and it happens to be exactly what makes an AI-assisted workflow fast and safe.

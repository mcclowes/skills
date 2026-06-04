Short answer: don't do the three-file smart/dumb/styles split. At 180 lines and one coherent concern, that pattern would make this file worse to work with through Claude Code, not better.

## Why the old instinct misfires here

The smart/dumb/styles split was calibrated for human scrolling and human navigation. A person flicks between four sibling files without thinking, holding the whole component in their head. An agent doesn't. It works with the file that's open and is reluctant to go read the siblings — so it makes confident edits based on partial context and breaks things it never looked at.

That changes the trade-off at exactly the boundary you're proposing:

- A **container + presentational split** for a form like this is the worst case. The presentational component's props are *shaped by the container*. An agent editing `CheckoutFormView.tsx` sees a `props` interface but can't tell where `savedCards` comes from, what shape the submit handler expects, or which states are even possible — all of that lives in the file it won't open. You'd get a "dumb" file that's clean but meaningless alone, and you've doubled the cross-file lookups the agent skips.
- The form state, the `useEffect` fetching cards, the submit handler, and the JSX all **change together and need each other for context**. Editing the saved-cards fetch usually means touching the state it populates and the JSX that renders it. That's the signal they belong in one file.

The decision test isn't "is this a separate concern?" It's "**can this concern be understood in isolation?**" Your JSX can't — it only makes sense alongside the state and handlers driving it. So co-locate.

## What I'd actually do

**Keep it as one file.** 180 lines of one cohesive component is comfortably under the threshold where signal-to-noise becomes a problem (roughly a few hundred lines). Cohesion beats line count. A self-contained 180-line file is a better prompt than three files that are each incomplete.

**Pull the styles out — that one's fine.** A styles/SCSS module is genuinely self-contained: it has no logic to understand and the agent rarely needs it in context to edit behavior. That split costs nothing. Do it if you like co-located styles; it's neutral either way.

**If you want to reduce noise, reach for an abstraction, not a file split.** The one part of this component that *can* stand on its own is the data + side-effect logic. Extract a `useSavedCards()` hook:

```ts
const { cards, loading } = useSavedCards();
```

That's a real abstraction, not just relocated code. It has an interface, it hides the fetch/effect/error handling, and the component reads the call site and knows enough to proceed without opening the hook. That genuinely shrinks the context needed to work on the rendering logic — which a file split does not.

You could do the same with the submit handler if it's gnarly (`useCheckoutSubmit()` returning `{ submit, submitting, error }`), but only if it earns a clean interface. If pulling it out leaves a hook that you can't understand without also reading the component, leave it inline.

## The rule of thumb

- Co-locate the form state, effects, handlers, and JSX. They're tightly coupled; splitting them just doubles lookups the agent won't do.
- Extract `useSavedCards()` (and maybe `useCheckoutSubmit()`) as hooks — abstractions, not files.
- Move styles to a module if you want; that one's genuinely isolatable.
- Revisit only when it crosses ~300 lines or starts covering distinct concerns. Split for signal-to-noise then, not out of reflex.

Net result: probably two files (component + styles) plus one or two hooks, instead of the old four-file ceremony. Each file stands on its own, which is the thing that actually matters when Claude Code is doing the editing.

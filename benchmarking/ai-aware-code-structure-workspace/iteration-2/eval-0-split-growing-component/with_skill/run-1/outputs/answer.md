Short answer: don't do the classic smart/dumb/styles three-way split here. At 180 lines this file is well within the range where keeping it together beats fragmenting it, and the specific split you're describing would actively hurt you given that most of your editing runs through Claude Code.

## Why the old instinct misfires now

The smart-container / dumb-presentational / styles pattern was calibrated for a world where the only readers were you and your teammates — humans who navigate a four-file component intuitively, glancing at the sibling file without a second thought. AI agents don't do that. They're stubbornly reluctant to open adjacent files. They work with what's in front of them and make confident edits based on the open file alone.

So when you split CheckoutForm into a container that shapes the props and a presentational component that consumes them, you create exactly the failure mode that bites hardest: the dumb component's props are defined by a sibling the agent won't open. Ask Claude to tweak the rendered output and it's working blind on how those props are actually shaped two files over. You've traded one coherent file for two that are each meaningless alone — and doubled the cross-file lookups the agent skips.

## The test to apply

Don't ask "is this a separate concern?" — form state, the fetch effect, and the submit handler obviously *are* separate concerns in the abstract. Ask instead:

> **Can this piece be understood in isolation?**

- The **JSX** in your form can't. It depends on the form state and the submit handler. Pull it into a presentational file and it references values shaped elsewhere — wrong boundary.
- The **state, effect, and submit handler** are tightly coupled to each other and to the markup. They orchestrate; they're meaningless apart. Splitting "smart" logic from rendering doesn't help when understanding either half requires the other.

This is the case the skill calls out explicitly: a smart unit that orchestrates state, effects, and data fetching is coupled by nature, and separating its logic from its rendering just creates two files that only make sense together.

## What I'd actually do

**1. Keep it as one file for now.** 180 lines of one coherent concern (a checkout form) is fine. The old "if it doesn't fit on a screen, split it" rule was about human scrolling; agents handle a few hundred lines comfortably before signal-to-noise degrades. Cohesion beats line count here.

**2. If you want to reduce what's in front of the agent, reach for an abstraction, not a file split.** The saved-cards fetch is the one genuinely separable piece — it has a clean interface (no input, returns cards + loading/error state) and can be understood without reading the rest of the form. Extract it into a hook:

```ts
const { cards, loading, error } = useSavedCards();
```

That's a *real* abstraction, not just relocated code. At the call site the agent reads `useSavedCards()` and knows enough to proceed without opening the hook's internals. That actually reduces the context needed to edit the form — which a file split never does, it only moves code around. The submit handler is a weaker candidate (it's coupled to form state), so I'd leave it inline unless it grows its own validation/error logic worth naming, e.g. `usePaymentSubmit()`.

**3. Styles: follow your existing convention, don't agonise.** A styles file (SCSS module / styled file) is a low-coupling split — the agent rarely needs the stylesheet open to reason about logic, and vice versa. If that's your house pattern, keep it. It's not the part that hurts.

## Where the line moves

If this file keeps growing — past ~300 lines, or it sprouts a second genuinely independent concern (say a full address form with its own validation) — then split. But split *then*, for the signal-to-noise reason, and split along a boundary where each side stands alone. Don't pre-emptively shatter a coherent 180-line component out of a reflex tuned for human scrolling.

So: extract `useSavedCards`, keep your styles file if that's your convention, leave the state + submit + JSX together in CheckoutForm.tsx. One self-contained file the agent can edit from a complete picture, with the one cleanly-isolatable concern lifted into a named hook.

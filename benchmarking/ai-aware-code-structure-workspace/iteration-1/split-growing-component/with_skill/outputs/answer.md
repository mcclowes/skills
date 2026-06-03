Short answer: don't do the classic three-way split. At 180 lines this is one coherent thing — a checkout form — and the smart/dumb/styles split would actively make it harder to work with, especially given that most of your edits go through Claude Code.

Here's the reasoning, then what I'd actually do.

## Why the smart/dumb/styles split is the wrong move here

The container/presentational pattern was calibrated for human readers who navigate multi-file components effortlessly — you glance at the sibling, hold the prop shapes in your head, jump between files without thinking. AI agents don't do that. They're remarkably reluctant to open adjacent files. They work with what's in front of them and make confident edits based on the open file alone.

That changes the trade-off. Picture the split you're describing:

- `CheckoutForm.container.tsx` — state, the `useEffect` fetching saved cards, the submit handler
- `CheckoutForm.view.tsx` — the JSX, driven by props
- `CheckoutForm.styles.ts`

Now you ask Claude Code to "add a billing address field." That touches state (container), the markup (view), and styling. The agent opens the view file, sees props it didn't shape, and either guesses at the container's structure or — more likely — edits the view in a way that's subtly wrong because it never checked how the prop was wired two files over. You've taken one self-sufficient file and turned it into three files that are each meaningless alone, and you've doubled the cross-file lookups the agent is least likely to perform.

The presentational file is the worst offender: its props are shaped entirely by the container. It can't be understood in isolation, which is exactly the test that matters.

## The test to apply

Not "is this a separate concern?" but: **can this concern be understood in isolation?**

Run it on your pieces:

- The **JSX** — its props, handlers, and state all live in the same component. Pull it out and it can't be understood or edited without reading the container back. Fails the test → keep it co-located.
- The state, the `useEffect`, the submit handler, and the markup are all the *same concern* (collecting and submitting payment details). They change together. Splitting them just scatters one idea across files.

A cohesive 180-line file that keeps logic and rendering together beats three small files that only make sense when read as a set. 180 lines is well within the range an agent handles comfortably — the rough ceiling where signal-to-noise starts to degrade is a few hundred lines, and you're not there.

## What I'd actually do: extract an abstraction, not files

If any part of this is earning its own home, it's the saved-cards data fetching — but the right tool is a **custom hook**, not a presentational split.

```tsx
// useSavedCards.ts
export function useSavedCards() {
  const [cards, setCards] = useState<SavedCard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    fetchSavedCards()
      .then((c) => !cancelled && setCards(c))
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, []);

  return { cards, loading };
}
```

Then `CheckoutForm.tsx` just calls `const { cards, loading } = useSavedCards();`.

This is genuinely different from splitting a file. A hook is a *real* abstraction: it has an interface, it hides its implementation, and the call site is understandable without reading the internals. When Claude Code is editing the form and sees `useSavedCards()`, it knows enough to proceed — it doesn't need the fetch logic in context. Splitting into container/view only *relocates* code; a hook actually *reduces* the context needed to work with the form. That's the win you're reaching for, and it gets it without scattering the prop wiring.

The same applies if the submit handler grows complex (validation, error mapping, retry) — extract `useCheckoutSubmit()` rather than a container. Abstraction before file structure.

## On the styles file

Splitting styles out is the least harmful of the three, and if your house style is SCSS modules it's probably what the rest of the codebase does — consistency wins there, so a `CheckoutForm.module.scss` is fine. Styles are low-coupling: an agent editing the form rarely needs to read the stylesheet to reason about behaviour, and vice versa. So that one's a judgement call on convention, not correctness. (If you're using inline/CSS-in-JS and the styles are short, leaving them in is also fine — don't split reflexively.)

## Concrete recommendation

1. **Keep `CheckoutForm.tsx` as one file** holding the form state, submit handler, and JSX. 180 lines of one coherent concern is not too big.
2. **Extract `useSavedCards()`** (and later `useCheckoutSubmit()` if the handler grows) into hooks — the saved-cards effect is the one piece that stands on its own behind a clean interface.
3. **Stylesheet:** follow your existing convention (a `.module.scss` sibling is fine), or leave styles inline if short.
4. **Skip the container/presentational split.** Revisit only if the file crosses ~300 lines or starts covering genuinely separate concerns — and even then, split along boundaries where each file stands on its own, not into a smart/dumb pair that has to be read together.

The general rule: structure for the reader you actually have. Most of your edits go through an agent that won't go looking across files, so co-locate what changes together and reach for abstractions (hooks) over file-splitting. The aggressive separation instinct from your earlier React years was the right answer for a human navigating files freely — it's the wrong default for an AI-assisted workflow today.

Short answer: don't do the three-way smart/dumb/styles split here. At 180 lines this is one coherent concern, and the split you're reaching for is calibrated for a human navigator, not for Claude Code.

## Why the old instinct misfires

The smart/dumb/styles pattern made sense when the main constraint was a human scrolling and holding the model in their head. They glance at the sibling file instinctively. An AI agent doesn't — it works with the file in front of it and is genuinely reluctant to go open adjacent files. So when you spread one component across a container, a presentational child, and a styles file, the agent editing the "dumb" view often can't see how its props are shaped (that lives in the container), and it makes confident changes that break.

The real test isn't "is this a separate concern?" It's **"can this piece be understood in isolation?"**

Run that on your four pieces:

- **Form state, the saved-cards `useEffect`, and the submit handler** all reference each other. The effect populates state, the handler reads it and calls the API, the JSX binds to it. Pull the logic into a "smart" file and the rendering into a "dumb" file and you get two files that are each meaningless alone — and you've doubled the cross-file lookups the agent won't perform. That fails the isolation test, so co-locate it.
- **A genuinely presentational sub-component** (props in, markup out, no side effects) *would* pass the test. If there's a chunk like that, it's a fine extraction. But that's the exception, not the default.

## What I'd actually do

**1. Leave it as one file for now.** 180 lines of cohesive checkout logic is comfortably within the range an agent handles well. The size ceiling worth worrying about is a few hundred lines, and you split at that point because signal-to-noise drops, not on reflex. Cohesion beats line count.

**2. If it feels busy, reach for an abstraction, not a file split.** This is the high-value move. The saved-cards fetch plus form state plus submit is a natural custom hook:

```ts
const { savedCards, values, setValue, submit, status } = useCheckoutForm()
```

That's a *real* abstraction, not just relocated code. At the call site the agent reads `useCheckoutForm()` and knows enough to render without reading the internals — it actually reduces the context needed, where a file split just moves code around. Your component file shrinks to the hook call plus JSX, and both the hook and the view stand on their own. This gets you most of the "separation of concerns" benefit you're after, but along a boundary that survives the agent's reluctance to look around.

**3. Styles: judgment call, low stakes.** A separate styles/SCSS-module file is the one piece that genuinely *is* understandable in isolation — it has no logic the agent needs to reason about — so co-locating vs. splitting it barely matters for AI editing. Follow your project convention. If you're using CSS/SCSS modules, a sibling `.module.scss` is fine. I wouldn't extract styles as part of a "proper architecture" ritual, but it's harmless either way.

## The boundary that matters

So: not three files split by *layer* (smart / dumb / styles), but at most two units split by *abstraction* — a `useCheckoutForm` hook with a clean interface, and the component that consumes it — plus a styles file if your conventions call for one. Each side can be understood and edited without opening the other, which is the actual test of a good split.

One caveat worth stating: this is a trade-off tuned to today's tools, not a permanent law. As agents get better at navigating across files, the threshold drifts back toward more aggressive separation. But structure for the tools you have now, and right now co-location plus a well-named hook beats a four-file spread.

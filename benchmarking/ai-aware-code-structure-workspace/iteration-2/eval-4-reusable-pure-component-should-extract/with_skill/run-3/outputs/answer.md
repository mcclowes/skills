Extract the shared `<Avatar/>`. The senior's instinct is a real one, but it's the wrong call for *this* shape of code.

## Why the "leave it inline" argument loses here

The fear is legitimate in general: AI agents are genuinely reluctant to chase imports, and a self-contained file is often a better prompt than one that scatters context across siblings. But that argument only wins when the cross-file lookup actually *costs* the agent something — when understanding the inlined code requires context that lives elsewhere.

Avatar is the exact opposite. It's a purely presentational unit: props in (`src`, `name`, `size`, `presence`), markup out, no side effects, no orchestration, no dependency on the host component's state. The test that matters isn't "is this a separate concern?" — it's **"can this concern be understood in isolation?"** Avatar passes that test trivially. An agent can open `Avatar.tsx`, see everything it needs, and edit it confidently with zero external context. That's the best-case file for an AI reader, not the worst.

So you're not trading "self-contained" for "chase an import." You're choosing between:

- **12 copies inline:** every host component carries 50 lines of avatar plumbing it doesn't care about. When an agent opens one of those files to do unrelated work, that's 50 lines of noise lowering the signal-to-noise of its context. And `<Avatar/>` at a call site is *more* self-documenting than 50 lines of raw markup — the agent reads the tag and knows what it does without parsing fallback-initials logic.

- **One `<Avatar/>` import:** the host files get shorter and more focused. The import is a real abstraction with an interface, not a relocated blob — it hides the implementation, so the consuming code is understandable without reading the internals.

## The part the senior is actually right about

The duplication is the bigger problem, and it's an AI-specific one. With 12 copies, when someone asks an agent to "fix the avatar fallback when the name is empty" or "add an `xl` size," it'll edit the one file it's looking at and leave the other 11 silently diverging. It has no way to know — and won't go looking for — the other copies. Twelve near-identical-but-drifting variants is precisely the kind of state agents handle badly. A single source of truth removes that failure mode entirely.

## Caveats so you extract it well

This only stays a clean win if the extracted component remains genuinely self-sufficient:

- **Keep it self-contained.** Props, types, and size variants all defined in (or imported into) the Avatar file itself. Don't shape its props from the host side. If a host has to be read to understand how Avatar is called, you've drawn the boundary wrong.
- **Co-locate its own pieces.** Styles, the size-variant map, and the initials-fallback helper live with the component — one file, not an Avatar split across four. A cohesive ~80-line Avatar file beats a "clean" four-file folder here; the few-hundred-line ceiling is nowhere near.
- **Don't over-abstract the API.** Resist a config-object mega-prop. A small, explicit prop list (`src`, `name`, `size`, `presence`) reads clearly at every call site, which is what makes the import cheaper than the inline copy.

## Bottom line

The senior's principle — favour self-contained files because agents won't chase context — is sound, and worth keeping for the cases it fits: smart, stateful components where logic and rendering only make sense together. Avatar isn't one of those. It's the textbook case for extraction: a pure, isolatable, repeated unit where the shared component is *both* the better abstraction for the AI and the cure for 12 copies drifting apart. Extract it.

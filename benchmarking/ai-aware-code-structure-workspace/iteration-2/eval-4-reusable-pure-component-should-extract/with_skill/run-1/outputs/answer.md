# Extract the shared `<Avatar/>`. The extract camp is right.

The "keep it inline so Claude sees everything self-contained" argument is a real instinct, and in some cases it's correct — but this is the textbook case where it's wrong. Here's the reasoning.

## Why the inline argument usually has merit

There's a genuine tension in AI-assisted codebases: agents are reluctant to look at adjacent files. They work with what's in front of them and make confident edits based on the open file alone. So a self-contained file often beats a "clean" one that's been shredded across four siblings the agent won't open. The senior isn't making this up.

But that argument applies to **tightly coupled** code — logic and rendering that only make sense together, props shaped two files over, types defined elsewhere. Splitting *that* just doubles the cross-file lookups the agent skips, and you get two files that are each meaningless alone.

## Why it doesn't apply here

Avatar is the exact opposite. Run the one test that matters:

> **Can this concern be understood in isolation?**

Yes, completely. It's pure presentation — props in (`src`, `name`, `size`, `presence`), markup out, no side effects, no orchestration, no data fetching. A standalone `Avatar.tsx` is self-documenting. An agent landing in that file has everything it needs with zero external context. This is the *best-case* candidate for its own file, not a marginal one.

And critically, extracting it doesn't create the problem the senior fears. The 12 consumers don't lose context — they *gain* a real abstraction. At each call site the agent reads:

```tsx
<Avatar src={user.avatarUrl} name={user.name} size="sm" presence={user.online} />
```

That single line is *more* legible than 50 lines of fallback-initials logic and presence-dot positioning inlined into a component that's actually about something else. The agent reads the call site and knows enough to proceed without ever opening `Avatar.tsx`. An abstraction reduces the context needed to work with the consumer — inline duplication bloats it.

So the import the senior wants to avoid isn't a cost here. `<Avatar/>` is named well enough that the agent rarely needs to chase it; the interface tells it everything. That's the difference between "split a file" (which just relocates code) and "extract an abstraction" (which actually hides implementation behind an interface).

## The cost the inline camp is ignoring

12 copies of ~50 lines is ~600 lines of duplicated markup. For an AI assistant specifically, that's actively harmful:

- **Inconsistent edits.** Ask Claude to "add an `xl` size" or "fix the presence dot offset" and it patches the open copy. The other 11 silently drift. Now you have 12 subtly different Avatars and an agent that can't tell which is canonical.
- **Noise in every host file.** Each of the 12 components carries 50 lines that aren't what that component is *about*. That's 50 lines of lowered signal-to-noise in 12 different prompts. The host components read worse, not better.
- **No single source of truth.** When the agent (or a human) needs to reason about "how do avatars work," there's no answer — there are 12 answers.

The self-contained-file benefit the senior wants is real, but Avatar already *is* a self-contained unit. Extraction gives you that benefit in one place instead of fighting duplication in twelve.

## Recommendation

Extract `<Avatar/>` into its own file. Keep it strictly presentational — props in, markup out, size/presence handled via props, no data fetching or store access inside it. Co-locate its styles and the small bits it owns (the initials-from-name helper, the size map) *in that same file* so the component itself stays self-sufficient and the agent never has to look around to edit it. Then replace all 12 inline copies with the import.

This is the rare refactor where every reader wins at once — human readability, maintainability, and machine readability all point the same way. The inline-for-AI heuristic is a good one to hold, but it's a tiebreaker for coupled code, and Avatar isn't coupled to anything.

One caveat to keep the senior happy: don't over-abstract it. Resist the urge to add a `variant` prop for every future need, a render-prop escape hatch, or a context provider. A flat, dumb, ~50-line `Avatar.tsx` with a clear prop interface is exactly right. The failure mode on the extract side is a clever, configurable Avatar that *itself* becomes the 300-line file nobody can read.

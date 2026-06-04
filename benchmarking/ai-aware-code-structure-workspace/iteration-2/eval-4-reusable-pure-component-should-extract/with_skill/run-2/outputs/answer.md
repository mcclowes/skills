Extract the shared `<Avatar/>`. The extract camp is right, and this is close to the cleanest case for it.

## Why the "keep it inline" argument doesn't hold here

The senior's instinct is a good one in general — AI agents are genuinely reluctant to chase imports, and a self-contained file is often a better prompt than one that scatters context across siblings. But that argument applies to a specific failure mode: a split that leaves each file dependent on the others to make sense. When an agent is parked in a "dumb" render file whose props are shaped by a sibling it won't open, the split has hurt you.

Avatar is the opposite of that. It's a **purely presentational** unit: props in (`src`, `name`, `size`, `presence`), markup out, no side effects, no state, no data fetching, no dependency on whatever component is hosting it. That's exactly the case the "understood in isolation" test is built to flag as a clean extraction:

- An agent opening `Avatar.tsx` needs almost zero external context. The props are the whole story; the file is self-documenting.
- An agent opening a host component sees `<Avatar name={user.name} size="lg" />` — a real abstraction with a name and an interface. It knows enough to proceed *without* reading the internals. That's strictly less context than 50 lines of fallback-initials and presence-dot logic inlined mid-component, which it has to read past every time.

So the import here doesn't cost the agent context — it *saves* it. The 50 lines of Avatar markup are noise relative to whatever the host component actually does (a profile card, a comment row, a member list). Inlining buries the component's real logic under boilerplate it has to skim every time it opens the file.

## The cost the inline camp is underweighting

Twelve copies is twelve places to edit when the design changes, and — more dangerous with AI in the loop — twelve copies that **drift**. An agent asked to "fix the presence dot alignment" will edit the one file it's looking at and leave the other eleven inconsistent, often without anyone noticing. Duplication is precisely the thing agents are bad at keeping in sync, because they don't go looking at the other eleven files any more than they'd chase an import. You don't escape the "won't look at other files" problem by inlining — you just convert it from one missing import into eleven silent divergences.

A single `<Avatar/>` with an interface is the *better* abstraction by the skill's own ordering: prefer a real abstraction (named, interfaced, implementation hidden) over file structure choices. This is that, exactly.

## The one thing that makes the extract worth doing well

The only legitimate kernel in the keep-inline view is the cross-file-context risk — so neutralize it by making Avatar genuinely self-contained:

- Keep its types **in the Avatar file** (`AvatarProps`, the `size` and `presence` unions), exported from there. Don't shape its props from a shared types file two directories away, or you've recreated the "agent won't open the sibling" problem.
- Co-locate its styles with it (same file or an adjacent module imported only by Avatar).
- Give it a clear, narrow interface so the call sites read as self-explanatory.

Do that and every reader — human, maintainer, and agent — gets the best of both: call sites that are lighter and clearer than the inline version, and an Avatar file an agent can open and edit with no context beyond its own props.

## Bottom line

Extract it. The "self-contained for the AI" goal is real, but inlining a pure, reusable component achieves the *opposite* of it — it spreads one concept across twelve files an agent will never reconcile, while bloating each host with boilerplate. A single `<Avatar/>` with its types and styles co-located is more self-contained, not less.

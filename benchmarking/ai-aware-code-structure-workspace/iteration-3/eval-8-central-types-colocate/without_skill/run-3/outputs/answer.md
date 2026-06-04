A single `types.ts` is one of the patterns that I'd actively move away from once you're editing mostly through Claude Code. It's not wrong, exactly, but it's optimised for an instinct ("one source of truth") that doesn't pay off the way you'd hope, and it quietly works against how an agent reads code.

## Why the central file feels clean but isn't

The appeal is real: one place to look, no duplicate definitions, easy to find a type by name. But "single source of truth" conflates two different things. The truth you care about is *the definition exists once* — not *all definitions live in one file*. A type defined next to the code that owns it is just as singular a source of truth as one in a shared file. You can keep the no-duplication property without the central file.

What the central file actually buys you is a table of contents. What it costs you is that the table of contents has no relationship to where the code lives.

## Why it's worse with an agent in the loop

The thing to know about Claude Code (and agents generally) is that they're reluctant to go look at other files. They work confidently from what's already in front of them and often won't proactively open a sibling to check how something is shaped. A central types file pulls *against* that grain in two ways:

- **Every meaningful edit becomes a two-file job.** When the agent is editing a service or component, the type it needs is never in the file — it's always one hop away in `types.ts`. Sometimes it makes that hop, sometimes it guesses, and guessing is where you get a confidently wrong change that doesn't match the actual shape.
- **When it does open `types.ts`, it pays for the whole thing.** It can't pull in just the one interface; the import drags the mental model of a 400-line grab-bag into context. Most of those 400 lines are irrelevant to the current task — pure noise competing for attention with the part that matters. Low signal-to-noise is exactly what degrades output quality.

So the file is simultaneously *too far* (the type isn't where the work is) and *too big* (when you reach it, it's mostly noise). That's the worst of both.

## What I'd do instead

Co-locate types with the code that owns them. The guiding test: **can this type be understood where it's used, without a hop the agent won't make?**

- **A type used by exactly one module → define it in that module's file.** A component's prop types, a service's internal shapes — these belong in the same file as the code, full stop. When the agent edits the component, the type is right there. No cross-file lookup, no guessing. This is the single highest-value move, and it'll cover a surprising share of those 400 lines once you look — a lot of "shared" types usually turn out to have one real consumer.
- **A type genuinely shared across a feature → put it in that feature's folder** (e.g. `features/checkout/types.ts`), near its consumers rather than in a global bucket.
- **Truly global types** — domain models imported everywhere, like `User` — *can* stay central, but split by domain (`types/user.ts`, `types/billing.ts`) rather than one omnibus file, so an import pulls in a coherent slice instead of everything.

The win is that the agent works from a complete local picture instead of a partial one, and each file it opens is mostly relevant to the task at hand.

## The honest caveats

- **Don't over-fragment.** The failure mode in the other direction is types so scattered that a shared one gets duplicated or you can't tell which file owns it. Co-location isn't "one type per file" — it's "the type lives with its owner." If a type has one clear owner, that's its home; if it has several, a feature-level or domain-level shared file is right.
- **400 lines isn't an emergency.** An agent handles a 400-line file fine in isolation. The problem here isn't the size of `types.ts` on its own — it's that it's the *forced second file* on nearly every edit, and a low-signal one. That's the case for moving things, not the raw line count.
- **Watch for circular imports** as you decompose — they're the usual reason teams retreat to a central file in the first place. If you hit cycles, that's a signal the dependency direction is off, not that the types belong in one bucket.

## Bottom line

Central `types.ts` optimises for a human skimming a directory; co-located types optimise for whoever — human or agent — is editing the code that uses them. Pull single-consumer types back into their modules, give shared types a feature-level home, and keep only the genuinely global ones central (and split by domain). You keep your real single source of truth and stop forcing a cross-file hop on every edit — which is exactly the hop Claude Code is most likely to skip.

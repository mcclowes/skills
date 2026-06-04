# Central types file: keep it, with caveats

Short version: a single `src/types.ts` is fine at 400 lines, and for an AI-edited codebase it's often better than the alternative. But the reason it's working isn't "single source of truth" as a principle. It's that types are unusually well suited to living together. Don't over-read the win.

## Why one file works well here, especially for Claude Code

Type definitions are the rare thing that's genuinely self-contained. A `type` or `interface` is props-in, shape-out, no side effects, no orchestration. Each declaration can be understood in isolation, which is exactly the test for whether code earns its own home. You could give every type its own file and each would stand alone fine.

So why does the *single* file beat the scattered version for an agent? Because the agent's biggest weakness is reluctance to look in other files. When types live in one place that everything imports, Claude already has the shapes it needs the moment it reads the import line. It doesn't have to go hunting through ten files to learn what a `User` or an `Order` looks like. One predictable location it can read once and hold. That removes the most common cross-file lookup an agent skips, which is the lookup that makes it confidently break things.

A pile of co-located, per-feature type files would actually be worse on this axis. More places to look, more chances the agent works from a partial picture.

## Where it stops being fine

Two failure modes, both about signal-to-noise rather than line count:

**The file becomes a junk drawer.** At 400 lines and "basically every component imports from it," you're near the point where the file stops being scannable as one coherent thing. The risk isn't size on its own. It's that a grab-bag of unrelated domains forces the agent (and you) to load the whole thing to use one corner of it. When you split, split by domain cohesion, not to hit a line target. `types/user.ts`, `types/billing.ts`, `types/api.ts`, each internally coherent. A barrel `types/index.ts` re-exporting them keeps the single, predictable import path the agent relies on, so you get the cohesion without scattering the entry point.

**Types that only make sense next to their code.** This is the real tell. A type tightly bound to one component or one function (a prop shape used in exactly one place, a discriminated union that mirrors one reducer) doesn't belong in the central file. It belongs next to the thing it describes, because changing the code and changing the type are the same edit. Pulling that type 400 lines away means every change is two files, and the agent does one and forgets the other. The heuristic: if a type is used in one place and changes whenever that place changes, co-locate it. If it's a shared contract crossing module boundaries, central file.

## What I'd actually do

1. Keep a central location for genuinely shared types, the contracts that cross boundaries between components and services. That's most of what makes a `types.ts` valuable.
2. Push single-use types back down next to the component or function that owns them. They're not shared, so they don't earn the shared file, and co-locating keeps each edit to one file.
3. If `types.ts` keeps growing or spans clearly separate domains, split it into a `types/` directory by domain and re-export through a barrel `index.ts`. Same import path, better signal-to-noise per file.
4. Don't split just because 400 feels big. 400 lines of cohesive type definitions is a fine file for an agent to read. Split when it's covering several unrelated domains, not when it crosses a line count.

The instinct that one source of truth felt clean is right for the shared contracts. Just make sure the file holds shared contracts, not every type in the app. The ones that belong to a single piece of code should live with it.

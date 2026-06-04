---
name: ai-aware-code-structure
description: Use when deciding how to organise code in an AI-assisted codebase — whether to split or merge a file, where to draw module boundaries, how big a file should get, whether to separate logic from rendering/styles/data, whether to use barrel/index re-export files, or where types and test files should live. Triggers on "should I split this file", "this file is getting too big", "separate concerns", "where should this code live", "are barrel files worth it", "central types file or co-locate", "colocate tests or a tests folder", reviewing or refactoring file/module organisation, structuring a new component or feature, or any architecture decision where part of the audience is an AI coding agent. Apply this whenever someone is choosing how to lay code out across files and an LLM will be reading or editing it, even if they only say "refactor this" or "clean up the structure" without mentioning AI.
license: MIT
metadata:
  author: mcclowes
  version: "1.0.0"
---

# AI-aware code structure

How to organise code across files when an AI coding agent is one of the readers. This is not "AI changes everything" — good, well-abstracted code reads well for humans and machines alike. But at the margins (how aggressively to split, how much to co-locate, how self-contained each file must be), AI shifts the trade-offs, and this skill is about getting those margins right.

## When this applies

Reach for this whenever the question is *where code lives*, not what it does: splitting a growing file, drawing a module boundary, deciding whether to peel logic out of a component, or reviewing an existing layout. It assumes an LLM will read or edit the result — which today is almost always true.

The examples here lean on React because that's where these questions surface most, but nothing in the reasoning is React-specific. It applies just as well to a Go package, a Python module, or a stylesheet.

## The core shift: a third reader

Code organisation has always balanced two readers: **human readability** (can someone understand this?) and **maintainability** (can it change safely?). AI adds a third: **machine readability** — can an agent operating in a limited context window understand and safely edit this?

For the most part these align. Clear structure with good abstractions serves all three. The interesting decisions are the ones where they pull apart.

## The limitation to design around

AI tools are remarkably reluctant to look at other files. They work with what's in front of them, and getting them to proactively explore adjacent files is like pulling teeth. A human navigates a four-file component intuitively — glances at the sibling, holds the model across files without thinking. An agent doesn't. It works with the open file and makes confident changes that break because it never checked how a prop was shaped two files over.

This produces a genuine tension, and both halves are real:

- **Focused files help.** Everything in context costs tokens and attention quality. A 60-line presentational component is a far better prompt than a 300-line file that does everything. High signal-to-noise → better output.
- **Split files hurt.** When a component is spread across four files and the agent is in one of them, it often lacks context it needs — props shaped elsewhere, types defined elsewhere, theme variables elsewhere. A beautifully focused file with insufficient context is worse than a slightly busier file that's self-sufficient.

The resolution isn't "split less" or "split more." It's to split along boundaries that survive the agent's reluctance to look around.

## The decision test

Don't ask *"is this a separate concern?"* Ask:

> **Can this concern be understood in isolation?**

That single question resolves most cases:

- A **purely presentational** unit — props in, output out, no side effects — is a great candidate for its own file. The agent can work on it with almost no external context; the file is self-documenting.
- A **"smart" unit** that orchestrates state, effects, and data fetching is tightly coupled by nature. Separating its logic from its rendering doesn't help if understanding either half requires the other — you've just created two files that are each meaningless alone, and doubled the cross-file lookups the agent won't perform.

So separation is still good — but the boundary has to be one where each side stands on its own.

## Heuristics

**Co-locate tightly coupled code.** If two pieces are always changed together and each needs the other for context, keep them in one file. This is the single highest-value move: it removes the cross-file lookup that an agent is most likely to skip, so it works from a complete picture instead of a partial one.

**Raise the file-size threshold.** The old rule — "if it doesn't fit on a screen, split it" — was calibrated for human scrolling. Agents handle larger files well, roughly up to a few hundred lines before quality degrades. A cohesive 150-line file that keeps logic and rendering together beats two 75-line files that are meaningless apart. There's still a ceiling: past ~300 lines signal-to-noise drops and you should split — but split for that reason, not out of reflex.

**Prefer abstractions over file structure.** A well-named custom hook (or function, or module) beats splitting files, because it's a *real* abstraction: it has an interface, it hides its implementation, and the consuming code is understandable without reading the internals. The agent reads `useCheckout()` at the call site and knows enough to proceed. Splitting a file only relocates code; an abstraction actually reduces the context needed to work with it. When tempted to split for readability, ask whether the right move is an abstraction instead.

**When you do split, make each side self-contained.** The test for a good split is whether each resulting file can be understood and edited without opening the others. If a file references props, types, or values that only make sense by reading a sibling, the boundary is in the wrong place — either move it or merge back.

## Three placement calls worth naming

The principles above settle most layout questions, but three specific ones come up constantly, and on each the AI-aware answer leans against a common human-era default. They're all the same move underneath: don't make the agent chase a definition across a boundary it won't cross.

**Barrel files (re-export `index.ts`).** A barrel that re-exports a folder reads nicely at the call site, but it inserts a hop on the exact axis agents are weakest. `import { Card } from '@/components'` no longer says where `Card` lives, so the agent either chases a wall of re-exports or, more often, guesses the component's shape and edits confidently wrong. Prefer direct paths (`@/components/Card`) that carry the address in the import itself. Keep a barrel only where it's a hand-curated public API at a real package boundary — there the barrel *is* the abstraction, naming what's public and hiding the rest. Direct imports also dodge the usual barrel costs: circular imports, broken tree-shaking, and slow test and dev-server startup.

**Where types live.** A central `types.ts` that everything imports is the sibling the agent won't open. Define a type next to the code that owns it, so changing the code and changing the type is one edit in one file, not two files where the agent does the first and forgets the second. Lift a type into a shared or feature-level file only when several modules genuinely share it, and keep the handful of truly global primitives central. "Single source of truth" means the definition exists once, not that all definitions live in one file.

**Test placement.** Put a unit test beside its source (`Foo.tsx` next to `Foo.test.tsx`), not in a `tests/` tree that mirrors `src/`. When the agent opens the source, a colocated test is right there in the directory listing, so it actually reads it, keeps it in sync, and uses it as a spec for how the code should behave. A mirrored tree puts maximum distance between the two, so the agent edits the source and never sees the test go stale. Keep a thin top-level dir only for cross-cutting integration or e2e tests that have no single home.

## Quick reference

| Situation | Lean toward |
|---|---|
| Pure presentation (props → output, no side effects) | **Separate** — self-documenting, low external context |
| Logic + rendering that need each other to make sense | **Co-locate** — splitting just doubles unperformed lookups |
| File growing but still one coherent concern, < ~300 lines | **Keep together** — cohesion beats line count |
| File past ~300 lines or covering several concerns | **Split** — signal-to-noise is now the problem |
| Tempted to split a file purely for readability | **Extract an abstraction** (hook/function/module) instead |
| A proposed split leaves files that only make sense together | **Don't split** — the boundary is wrong |
| Barrel / re-export `index.ts` for a folder's internals | **Direct imports** — keep a barrel only at a real public-API boundary |
| A type used by a single module | **Co-locate** it with that module, not a central `types.ts` |
| Unit test for one source file | **Beside the source**, not a mirrored `tests/` tree |

## Applying this skill

- **Deciding whether to split a file:** run the "understood in isolation?" test on each proposed piece. If a piece can't stand alone, co-locate it. Recommend an abstraction before recommending a split.
- **Reviewing organisation:** look for splits that force cross-file context — the most common smell is a "dumb" render file whose props are shaped by a sibling the agent won't open. Flag files split below the human-era size reflex with no isolation benefit.
- **Structuring something new:** start coarser than the old instinct suggests. Let files grow to a few hundred lines while they stay coherent, and reach for an abstraction (not a new file) when one part earns a real interface.

This is a current trade-off, not a permanent law. The reluctance to read adjacent files is a limitation of today's tools, not a fundamental one — as agents get better at navigating codebases, the threshold will drift back toward aggressive separation. Structure for the tools you have.

# Barrel files in an AI-edited React + TypeScript app

Short version: the import ergonomics are nice, but barrel files are mostly working against you now, and the "big `src/components/index.ts`" is the part I'd kill first. I'd keep a couple of narrow, deliberate barrels at genuine package boundaries and drop the rest. Here's the reasoning, because the trade-off isn't obvious and it's changed.

## What a barrel file actually is, in context terms

`import { Button, Modal, Card } from '@/components'` is pleasant to write. But that one import line points at an `index.ts` that re-exports the whole folder. The convenience is real for the human typing the import. The cost is paid somewhere the human doesn't see: by anything that has to *resolve* that line — the bundler, the type checker, the test runner, and increasingly the agent trying to understand where `Button` lives.

The pattern optimises the one thing that was never the bottleneck (typing import paths) and taxes the things that are (build/test speed, and an agent's ability to trace code without spelunking).

## Why it hurts more with Claude Code and Cursor

The core limitation to design around with these tools: **agents are reluctant to look at other files.** They work confidently with what's in front of them and don't proactively explore. A barrel file inserts a layer of indirection at exactly the spot where that reluctance bites.

Concretely:

- **It breaks "go to where this came from."** When an agent sees `import { Button } from '@/components'`, the honest answer to "where is Button defined?" is two hops away: open the barrel, find the re-export line, then follow that to the real file. A direct `import { Button } from '@/components/Button'` answers the question in the import itself. With direct paths the agent often doesn't need to open anything; it knows enough to proceed. With a barrel it either does extra lookups (slow, and it's bad at this) or — more commonly — guesses, and guesses are where confidently-wrong edits come from.
- **It pollutes context when the agent *does* follow the trail.** Open `src/components/index.ts` and you get a wall of re-exports for the entire component library — dozens of names, none of which help with the task at hand. That's pure noise in the context window. High signal-to-noise produces better output; a big barrel is structurally low signal.
- **Indirection compounds.** Folder-level `index.ts` re-exporting into a top-level `index.ts` means tracing a symbol can be three hops, not one. Each hop is a file the agent has to choose to open. Every hop is a chance to stop early and hallucinate the shape of something.

None of this is unique to AI — barrel files have well-known downsides for humans too (see below). AI just removes the one thing that made them feel worth it. A human navigates the indirection intuitively and holds the model across files without thinking. An agent doesn't, so the indirection is close to pure cost.

## The non-AI costs are also real (and worth saying)

So this isn't only an "AI made me do it" argument:

- **Bundle and tree-shaking hazards.** A big barrel encourages the bundler to pull in (or at least analyse) the whole module graph behind it. Side-effectful modules behind a barrel can defeat tree-shaking entirely. It's a classic source of "why is my entry chunk so big" and of accidental eager-loading.
- **Build and test-watch slowness.** Importing one thing through a barrel makes the type checker and dev server consider everything the barrel touches. On large component sets this is a measurable hit to TS server responsiveness and HMR — the exact inner-loop latency you feel all day in Cursor.
- **Circular-dependency traps.** Folder barrels are a reliable way to manufacture import cycles (A imports the barrel, the barrel re-exports B, B imports the barrel...). These produce baffling `undefined`-at-runtime bugs that neither you nor the agent will enjoy debugging.

## What I'd actually do

This isn't all-or-nothing. Barrels at a *real* boundary are fine; barrels-by-reflex on every folder are the problem.

**1. Delete the big `src/components/index.ts`.** This is the worst offender on every axis: largest noise surface, deepest indirection, biggest tree-shaking liability. Switch call sites to direct paths:

```ts
import { Button } from '@/components/Button'
import { Modal } from '@/components/Modal'
```

Yes, it's more import lines. That cost is paid by a human glancing at the top of a file — cheap. The savings are paid out to the bundler, the type checker, and every agent edit — the expensive readers.

**2. Drop the per-folder `index.ts` re-exports too, by default.** For a `Button/` folder, `import { Button } from '@/components/Button'` resolving to `Button.tsx` (or `Button/Button.tsx`) is one clear hop with no barrel needed. Make the path point at the real file. The agent can read the import and know exactly what file to open and edit.

**3. Keep barrels only where there's a true package boundary with a deliberately curated public API.** A shared design-system package that publishes a controlled surface (`@acme/ui`) is a legitimate use: the barrel *is* the API contract, it's intentional, and consumers genuinely shouldn't reach past it. The test is whether the barrel exists to *hide* internals behind a real interface, or merely to *relocate* exports for typing convenience. The first is an abstraction worth keeping; the second is indirection with no payoff.

**4. If you keep any barrels, make them type-only or side-effect-free and mark them.** Set `"sideEffects": false` appropriately and prefer `export type` re-exports where you can, so at least the tree-shaking and circular-dependency risks are contained.

## The honest counter-argument

Two reasons you might keep more than I'm suggesting:

- **Refactor churn.** Direct paths mean moving a file updates more import sites. In practice this is a non-issue: it's a mechanical rename your IDE and the agents both do reliably, and it's a one-time cost versus a daily tax.
- **Public-surface discipline.** If barrels are how you enforce "don't import internals," that's a real benefit — but enforce it only at the boundaries that deserve a public API (point 3), not at every folder.

## Bottom line

The barrel pattern is hurting more than helping in an AI-edited codebase, and the costs aren't only AI ones — it's a long-standing bundling and build-latency liability that AI tooling has tipped from "nice convenience" to "net negative." Kill the big `src/components/index.ts` first, drop per-folder barrels as the default, and keep barrels only where one genuinely guards a curated public API. You'll trade slightly longer import lines (paid by humans, cheaply) for faster builds, cleaner tree-shaking, fewer cycles, and edits the agent can make without guessing where anything lives.

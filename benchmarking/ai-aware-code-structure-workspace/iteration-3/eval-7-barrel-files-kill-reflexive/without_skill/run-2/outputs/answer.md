# Barrel files in an AI-edited codebase

Short version: the barrel pattern is mostly hurting you, and I'd retire the big aggregator barrels (`src/components/index.ts`) while being more selective about the per-folder ones. It's a low-risk change with a real upside for both your tooling and your build.

The thing to notice is that barrel files trade away the property that matters most when an agent is your main editor: **a clear, traceable path from a usage back to the definition.**

## Why it reads well to humans but works against agents

`import { Button, Modal, Card } from '@/components'` is pleasant for a person — it's tidy and you don't think about paths. But it deliberately hides where each symbol actually lives. A human doesn't care because they'll cmd-click through, or they already hold the layout in their head.

An agent behaves differently. The single most important limitation to design around is that AI tools are remarkably reluctant to look at other files — getting them to proactively explore adjacent files is like pulling teeth. A barrel sits directly across that path:

- To find `Button`'s real definition, the agent has to open `components/index.ts`, parse a wall of re-exports, find the line, then follow it to the source. That's two extra hops on top of the hop it didn't want to take in the first place. In practice it often won't, and works from a guess about the component's props instead — which is exactly how confident-but-wrong edits happen.
- The barrel file itself is pure noise as a prompt. A 200-line `index.ts` that is nothing but `export * from './Button'` lines is the worst kind of context: it costs tokens and attention while telling the agent almost nothing about behaviour.
- When the agent *adds* a component, it now has to remember to update the barrel too — a second, easily-skipped edit in a file it never opened. Half-wired exports are a common result.

So the pattern fails the test I'd apply here: it inserts a mandatory cross-file lookup precisely where the tool is least willing to perform one, and the file it forces you through carries no real signal.

## It's not only an AI problem

The barrel concerns predate agents, and they reinforce the call:

- **Circular imports.** Big barrels are the classic source. `A` imports from `@/components`, which re-exports `B`, which imports from `@/components`... these cycles are miserable to debug and agents are particularly bad at reasoning about them.
- **Bundle / tree-shaking.** `export *` aggregators routinely defeat tree-shaking and balloon what gets pulled into a chunk. They're also a known cause of slow cold starts and slow test runs (importing one component drags in the whole barrel's transitive graph). In a Next.js app this is a real cost; `optimizePackageImports` exists specifically because barrels hurt.
- **Reasoning about blast radius.** "What uses `Modal`?" is answerable by grep when imports point at `@/components/Modal`. Route everything through one barrel and every importer looks identical, so neither you nor the agent can see the true dependency edges.

## What I'd actually do

**1. Drop the big aggregator barrel (`src/components/index.ts`).** This is the one doing the most damage — biggest noise file, most likely to spawn cycles, worst for tree-shaking. Switch to path imports:

```ts
import { Button } from '@/components/Button'
import { Modal } from '@/components/Modal'
```

Slightly more verbose, but every import line is now a working address the agent can follow in one hop. This is the highest-value change.

**2. Be selective about per-folder `index.ts` files.** They're not all equal:

- A **genuine module with a real public API** — say `components/DataTable/` with `DataTable` plus its `Column`, `Row` helpers, where the folder is the unit you consume — a small, hand-written `index.ts` that exports only the intended surface is fine and even useful. It's a real abstraction: it names an interface and hides internals. Keep these, but write them explicitly (`export { DataTable } from './DataTable'`), not `export *`.
- A **folder that's one component plus its parts** doesn't need a barrel at all. Import the file directly. The barrel adds a hop and buys nothing.

The line is the same one I'd use for any split: does the barrel expose a coherent, self-contained interface, or is it just a passthrough? Keep the former, delete the latter.

**3. If you keep any, ban `export *` and re-exported types-as-values.** Explicit named re-exports avoid the circular-dependency and tree-shaking traps and keep the file readable as an actual API surface.

## Migration is cheap and agent-friendly

This is close to mechanical: a codemod (jscodeshift / ts-morph) or even your editor's "update imports" can rewrite `from '@/components'` into per-path imports by resolving each name through the existing barrel. Do it per-folder, lean on the type-checker to catch stragglers, and delete each barrel once nothing imports from it. You can even hand this to Claude Code folder by folder — it's the kind of well-bounded refactor agents do reliably.

## The one real cost

You lose the tidy one-line import and the ability to swap an implementation behind the barrel without touching callers. In practice that indirection is rarely exercised, and when you genuinely have a module with a stable public API, a small explicit barrel for *that module* gives you the same benefit without the app-wide aggregator's downsides.

## Bottom line

Keep small, explicit, hand-written barrels for the few folders that are real modules with a public API. Kill the big `src/components/index.ts` aggregator and any per-folder barrel that's just a passthrough. Direct path imports give the agent a traceable definition in one hop, kill a class of circular-import and tree-shaking problems, and make your dependency graph greppable again. The verbosity you trade for it is the cheap part.

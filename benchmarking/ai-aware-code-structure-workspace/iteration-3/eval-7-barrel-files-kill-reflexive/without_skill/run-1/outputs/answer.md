# Barrel files in an AI-edited React + TS app

Short version: barrel files are mostly hurting you, and the harm gets worse the more your editing happens through Claude Code and Cursor. I'd unwind the big aggregating barrels and keep, at most, a few deliberate ones at true public boundaries. Here's the reasoning, because the "would you keep it" answer depends on *which* barrel.

## Why barrels were appealing

The pitch is real: `import { Button, Modal, Card } from '@/components'` reads nicely, import lines stay short, and you can move a file without touching every call site. For a human skimming a diff, one tidy import block is pleasant.

But almost every one of those benefits is a *human-ergonomics* benefit, and several of them quietly invert once an agent is the primary editor.

## Where it hurts, specifically with AI tools

**1. The barrel is an indirection layer the agent has to hop through.**
The single biggest limitation of today's agents is that they're reluctant to look at adjacent files. They work with what's in front of them. A barrel inserts a mandatory extra file between "I see `Card` used here" and "here's where `Card` actually lives." When an agent wants to read or edit `Card`, it sees `@/components`, opens `src/components/index.ts`, and now has to resolve which re-export line leads to the real file — an extra lookup, on exactly the axis where agents are weakest. Direct paths like `@/components/Card` tell the agent where the code is *in the import itself*. That's strictly better for a machine reader.

**2. A big `src/components/index.ts` is low signal-to-noise as context.**
When the agent does open that barrel — and it will, chasing a symbol — it gets a wall of re-export lines for the entire component library, almost none relevant to the task. That's tokens and attention spent on noise. Compare to a direct import that resolves to one focused file. This is the same principle as keeping files focused: a 60-line presentational file is a great prompt; a 200-line re-export manifest is a terrible one.

**3. Barrels manufacture false coupling and circular-import traps.**
This is the one that actually bites in production, not just in theory. `import { Button } from '@/components'` pulls in the *whole* module graph behind the barrel, because the barrel references everything. So:
   - **Agents reach for the wrong thing.** Since everything is exported from one name, an agent editing `Modal` can frictionlessly `import { someInternalHelper } from '@/components'` that was never meant to be public. The barrel erases the distinction between "public API of this folder" and "internal detail," so agents (and humans) wire up dependencies that shouldn't exist.
   - **Circular imports.** Folder A's barrel re-exports something that imports from folder B's barrel that re-exports something importing from A. These cycles are miserable to debug, and an agent that won't traverse files is poorly placed to diagnose them — it'll often "fix" the symptom by adding another import and deepen the cycle.

**4. Tooling and performance costs that compound under heavy editing.**
Barrels defeat tree-shaking unless your bundler is perfectly configured (importing one symbol can drag in the whole barrel's graph), they slow cold dev-server and test startup, and they blunt "go to definition" / find-references. Under an AI workflow you're running tests and rebuilds constantly, so the startup tax is paid often. Vite, Jest/Vitest, and Next all have known barrel-related slowdowns at scale.

**5. The "easy to move files" benefit barely materialises.**
The classic argument for barrels is that consumers don't break when you reorganise internals. But both Claude Code and Cursor do project-wide rename/refactor and grep-style edits trivially. The cost barrels were designed to avoid — updating import paths — is now nearly free, while the costs they impose (indirection, false coupling, cycles) are paid every time the agent reads code. The trade has gone underwater.

## Run it through the real test

The question I'd actually ask isn't "is this a separate concern?" but **"can this be understood in isolation?"** A direct import `@/components/Card/Card` passes: the path tells you what it is and where it lives, and the agent lands directly on a self-contained file. The barrel import fails it: `@/components` tells you nothing about which file, forces a hop through a noisy manifest, and obscures whether you're touching a public or internal symbol.

## What I'd keep

This isn't "barrels are always evil." There's one legitimate use: a **single, deliberate, public-API barrel at a real boundary** — e.g. a shared design-system package or a feature module that genuinely exposes a curated surface to the rest of the app. There, the barrel *is* the abstraction: it documents "these N things are public, everything else is internal," and that constraint is valuable for both humans and agents. Keep those, and make them hand-curated, not "re-export everything."

What I'd drop:
- The reflexive `index.ts` in **every** folder. Most of those export one or two things and exist only out of habit. They add a hop and buy nothing.
- The big aggregating `src/components/index.ts` that re-exports the entire library. This is the worst offender on every axis above.

## Concrete recommendation

1. **Delete the per-folder barrels** that just re-export a single component, and switch their consumers to direct paths (`@/components/Button/Button` or `@/components/Button`). This is a mechanical, agent-friendly refactor — exactly the kind Cursor/Claude Code do well, so the migration cost is low.
2. **Replace the monolithic `src/components/index.ts`** with direct imports. If you want to soften the diff, do it folder-by-folder.
3. **Keep at most a few intentional barrels** at genuine package/public-API boundaries, curated by hand.
4. **Add an ESLint guard** (`no-restricted-imports`, or `eslint-plugin-import` rules like `no-cycle`) to stop new everything-barrels creeping back and to catch the circular imports the old pattern was hiding.

Net: the barrel pattern optimises for a human reading import blocks, at the expense of the machine reader doing most of your editing now — adding indirection, noise, false coupling, and build-time cost. Trade the convenience for direct imports everywhere except a small number of deliberate public boundaries.

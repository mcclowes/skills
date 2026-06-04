# Barrel files in an AI-edited React + TS app

Short version: the barrel-everywhere pattern is hurting you more than helping, and now that almost all editing goes through Claude Code and Cursor, that's the deciding factor. I'd drop the per-folder `index.ts` re-exports and the big `src/components/index.ts`, and switch to direct imports. Keep barrels only at genuine public-API boundaries (a published package, or a deliberately-sealed module).

## Why barrels specifically hurt with AI editing

A barrel reads nicely at the call site — `import { Button, Modal, Card } from '@/components'` is tidy — but it inserts a hop on the exact axis AI agents are weakest. These tools are remarkably reluctant to open adjacent files. They work with what's in front of them and make confident edits from that.

With `import { Card } from '@/components'`, the import line no longer tells the agent *where* `Card` actually lives. So one of two things happens:

- It chases a wall of re-exports through `index.ts` to find the real file (extra hops, extra tokens, and it often won't bother), or
- More commonly, it guesses `Card`'s props/shape from the name and edits confidently wrong.

A direct import — `import { Card } from '@/components/Card'` — carries the address in the import itself. The agent knows the file to open without any lookup. The path *is* the documentation. That's the single biggest win here: every import becomes a map to the source.

## The non-AI costs you're also paying

Even setting agents aside, the pattern has well-known downsides that compound at scale:

- **Circular imports.** A big `src/components/index.ts` that re-exports everything is a classic source of import cycles, which are miserable to debug.
- **Broken tree-shaking.** Pulling one component through a barrel can drag the whole barrel's dependency graph into the bundle unless your tooling is perfectly configured.
- **Slow startup.** Barrels are a known cause of sluggish test runs and dev-server cold starts — importing one thing eagerly evaluates the whole re-export chain. In a large app this is often seconds per test file.

Direct imports dodge all of these for free.

## What I'd keep

Barrels aren't categorically bad — they're an abstraction, and they earn their place at a *real boundary*. Keep one where:

- You publish a package and the barrel is its **hand-curated public API** — it names what's exported and hides the rest. There the barrel *is* the contract.
- You have a module you want to seal deliberately so consumers can't reach into its internals.

The test: is this barrel a curated public surface someone designed, or is it a reflexive "every folder gets an `index.ts`" that just re-exports whatever happens to be in the directory? The first is worth keeping. The second — which is what you've described — is the one to remove.

## Concrete recommendation

1. **Delete the per-folder `index.ts` re-export files** that exist only to forward a directory's contents, and the big `src/components/index.ts`.
2. **Switch to direct imports** (`@/components/Card`, `@/components/Modal`). This is highly mechanical — a codemod or even find-and-replace handles most of it, and the TypeScript compiler will flag anything you miss.
3. **Keep a barrel only where it's a designed public API** at a package boundary.

This is a great task to hand to the agents themselves: the change is large but low-risk, and the type checker is your safety net.

One caveat worth naming: this is a trade-off calibrated to *today's* tools. The reluctance to read adjacent files is a current limitation, not a law of nature. If agents get markedly better at navigating codebases, the cost of barrels drops and the readability argument gets stronger again. But structure for the tools you have now — and right now, direct imports win.

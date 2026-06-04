## Short answer

Hurting you, mostly. I'd drop the per-folder `index.ts` barrels and the big `src/components/index.ts`, and switch to direct imports like `import { Button } from '@/components/Button'`. Keep a barrel only if and where it's a deliberately curated public API at a real package boundary (more on that below).

## Why barrels work against you specifically

Since you do almost all editing through Claude Code and Cursor, the cost that matters most isn't bundle size — it's that **AI agents are reluctant to look at files that aren't already open**. They work confidently with what's in front of them and rarely go chase a definition across a hop they don't have to.

A barrel inserts exactly that hop, on the axis where agents are weakest:

- `import { Button, Modal, Card } from '@/components'` no longer tells the agent *where* `Button` lives. The import has lost its address.
- To work on `Button`, the agent now has to walk the wall of re-exports in `src/components/index.ts` to find the real file. In practice it often doesn't — it guesses the component's shape and props and edits confidently wrong.
- A direct path, `@/components/Button`, carries the location in the import itself. The agent reads the import and knows where to go. No lookup it might skip.

So the thing that reads nicely at the call site for a human is precisely the thing that starves an agent of the one cheap signal it had — the file path.

## The non-AI costs you're also paying

Even setting the agents aside, big aggregating barrels tend to bring:

- **Circular imports** that are maddening to debug, because everything routes through one hub.
- **Broken or degraded tree-shaking** — importing one thing from `@/components` can drag the whole barrel into the graph.
- **Slow dev-server and test startup**, since touching the barrel pulls in every component transitively. This compounds in watch mode and in test files that import from the barrel.

These get worse as `src/components/index.ts` grows, which it will.

## The one case worth keeping

A barrel earns its place when it *is* an abstraction: a hand-curated public API at a genuine package boundary. If you publish a design-system package and want consumers to write `import { Button } from '@your-org/ui'` while everything else stays private, that single top-level barrel is doing real work — it names what's public and hides the internals. That's a deliberate interface, not a reflexive re-export of a folder.

The test: is the `index.ts` a curated list of "this is the public surface," or is it just `export * from './everything'` for every folder? The first is an abstraction worth keeping. The second is the reflexive pattern to remove.

## What I'd actually do

1. Kill the per-folder `index.ts` files that just re-export their own contents. Those buy you nothing and cost you the address on every import.
2. Replace the big `src/components/index.ts` with direct imports at call sites (`@/components/Button`, `@/components/Modal`, …). A codemod or even a careful find-and-replace handles most of this; `ts-morph` or `eslint-plugin-import` rules can enforce "no importing from the barrel" afterward.
3. Keep exactly one curated barrel only if you have a real package boundary (e.g. a shared UI lib consumed by other apps). If you don't have that boundary, you don't need any barrel.

The migration is mechanical and low-risk, and it pays off every time an agent edits a component — which, for you, is most of the time.

One caveat worth naming: this is a trade-off calibrated to today's tools. The reluctance to read adjacent files is a current limitation, not a law of nature. If agents get reliably good at navigating imports, the calculus softens. But structure for the tools you actually have, and right now those tools read the path and trust it.

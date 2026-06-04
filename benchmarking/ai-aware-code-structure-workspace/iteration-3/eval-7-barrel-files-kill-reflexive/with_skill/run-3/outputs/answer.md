# Barrel files in an AI-edited codebase

Short version: the reflexive, every-folder-has-an-`index.ts` pattern is hurting you more than helping, and now that most editing goes through Claude Code and Cursor, it's hurting you on the exact axis those tools are weakest. I'd drop it for internal re-exports and keep barrels only at real package boundaries.

## Why barrels read nicely but work badly with agents

`import { Button, Modal, Card } from '@/components'` is pleasant for a human skimming a file. But it throws away the one thing an AI agent needs most: the address. The import no longer says where `Card` lives.

The core limitation to design around is that AI tools are remarkably reluctant to look at other files. They work with what's in front of them, and getting them to proactively chase a definition across files is like pulling teeth. A barrel inserts a hop on precisely that axis. When the agent needs to know what `Card` accepts, it has two options:

1. Chase the re-export — open `src/components/index.ts`, find the line, follow it to the real file. Agents often won't.
2. Guess the shape of `Card` from the call site and edit confidently wrong.

Option 2 is the common one, and it's how you get changes that look right and break, because the agent never saw the actual prop types two files over. A direct import (`@/components/Card`) carries the address in the import itself, so the agent already knows where to look and is far more likely to actually look.

## The other costs (these aren't AI-specific, but they compound)

Big internal barrels — especially that central `src/components/index.ts` — also bring the classic problems:

- **Circular imports.** A central barrel makes it easy for two components to import each other through the barrel and form a cycle that's painful to untangle.
- **Broken tree-shaking.** Importing one thing through a barrel can pull the whole module graph into a bundle.
- **Slow startup.** Test runners and dev servers have to evaluate the entire barrel (and everything it touches) just to resolve one symbol, which shows up as sluggish Vitest and dev-server boot times.

So you're paying a real build/test tax for the privilege of giving the agent a worse map.

## What I'd actually do

**Replace internal barrels with direct imports.** `import { Card } from '@/components/Card'`. Each import now states exactly where the thing lives. This is the high-value change and it's mechanical — codemod-able with `eslint-plugin-import` rules or a quick find-and-replace, and your tooling/CI will catch stragglers.

**Keep a barrel only where it's a hand-curated public API at a real boundary.** If `@/components` is a genuine published or semi-published surface — a design-system package that the rest of the app consumes as a black box — then a barrel there is doing real work: it *names what's public and hides the rest*. There the barrel is the abstraction, not just a relocation of exports. The test is whether the `index.ts` is a deliberate, curated list ("this is our public API") versus an auto-generated `export * from './everything'`. Curate-and-keep the former; delete the latter.

**Don't auto-generate barrels per folder.** The every-folder `index.ts` habit is the reflex to kill. A folder's internals aren't a public API; they're implementation, and the agent benefits from seeing the real paths.

## One caveat

This is a trade-off calibrated to today's tools, not a law of nature. The reluctance to read adjacent files is a limitation of current agents; as they get better at navigating codebases, the cost of a barrel hop will shrink. But you're optimising for the tools you have right now, and right now direct paths give Claude Code and Cursor a materially better picture to edit from.

**Recommendation: drop the reflexive per-folder and central barrels, move to direct imports, and keep a curated barrel only if `@/components` is a true package boundary you treat as a black box.**

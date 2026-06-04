Yes, it matters, and I'd colocate. `Foo.test.tsx` next to `Foo.tsx`.

## Why it matters more when Claude Code is the main editor

The deciding factor isn't human ergonomics here, it's that AI agents are reluctant to look at adjacent files. They work with what's in the open file and make confident edits from a partial picture. A mirrored `tests/` tree is the worst case for that behaviour: the test and the code it covers are maximally far apart in the file tree, with no proximity cue telling the agent the test exists.

Concretely, with a separate `tests/` directory:

- When you ask Claude to change `Foo.tsx`, it edits the source and often never opens `tests/.../Foo.test.tsx`. The test silently goes stale or breaks, and you find out at CI time instead of in the loop.
- When you ask it to add a test, it has to reconstruct the mirror path (`src/widgets/Foo.tsx` to `tests/widgets/Foo.test.tsx`) and frequently gets it slightly wrong, or dumps the test in the wrong place.
- Refactors that move a file leave the test orphaned, because the agent doesn't track the parallel tree.

Colocation fixes all three. When `Foo.test.tsx` sits beside `Foo.tsx`, the test is right there in the directory listing the agent already sees. It's far more likely to open it, update it alongside the change, and put new tests in the obvious spot. The convention is also self-evident from the file structure, so the agent doesn't have to be told the mapping.

This is the same principle as colocating tightly coupled code: a unit test and its subject change together and each needs the other for context. The mirrored-tree split is exactly the kind of boundary that doubles the cross-file lookups an agent won't perform.

## The honest caveats

- This applies cleanly to **unit and component tests** that target a single source file. Integration, e2e, and cross-cutting tests don't have a natural neighbour, so keep those in a top-level `tests/` (or `e2e/`) directory. A hybrid is normal and correct: colocated unit tests, separate dir for the broad stuff.
- Vitest needs no config change to find colocated tests. The default `include` glob (`**/*.{test,spec}.?(c|m)[jt]s?(x)`) already picks them up wherever they live.
- If you ship the package and care about bundle hygiene, make sure your build/`tsconfig` excludes `*.test.*` (most setups already do, and `tsup`/Vite handle this fine). For an app rather than a library this is a non-issue.
- Some people dislike the visual noise of test files interleaved with source. That's the main argument the other way, and with an agent doing most of the editing it carries little weight. You can mitigate it with editor file-nesting (VS Code nests `Foo.test.tsx` under `Foo.tsx`) if it bothers you.

## What I'd do

1. Adopt colocation for unit/component tests going forward.
2. Keep (or create) a top-level `tests/` or `e2e/` only for integration and end-to-end tests.
3. Migrate the existing mirror lazily: move each test next to its source the next time you touch that area, rather than one big churning PR. Claude Code can do the moves file-by-file as you go, and you avoid a giant rename diff that's hard to review.

The migration has a real cost, so it's not worth a stop-the-world effort, but the steady-state win, fewer stale tests because the agent actually sees them, is worth steering toward.

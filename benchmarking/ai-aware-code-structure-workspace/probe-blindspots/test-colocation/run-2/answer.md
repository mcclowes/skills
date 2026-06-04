Colocate them. `Foo.tsx` beside `Foo.test.tsx`. Move off the mirrored `tests/` tree.

## Why it actually matters here

The choice usually gets argued on taste, but the way you work tips it decisively. You edit through Claude Code, and the single most reliable behaviour of an AI agent is that it works with the file in front of it and is reluctant to go hunting for siblings. A mirrored `tests/` tree puts the test at `tests/components/Foo.test.tsx` while the source sits at `src/components/Foo.tsx` — a different path in a different subtree. That's exactly the cross-file lookup the agent tends to skip.

Concretely, colocation buys you:

- **The agent sees the test exists.** When it opens `Foo.tsx` to make a change, `Foo.test.tsx` is right there in the same directory listing. It's far more likely to read the test, respect the contract, and update it alongside the change. With a mirrored tree, the test is out of sight and routinely goes stale — the agent edits the source, never opens the test, and you find out in CI.
- **Renames and moves stay coherent.** Move or rename a component and the test travels with it. In a mirrored tree the two paths drift independently, and you accumulate orphaned tests pointing at code that moved.
- **The relationship is unambiguous.** `Foo.tsx` / `Foo.test.tsx` is a self-describing pair. No mental mapping between two parallel trees, for you or the agent.

## Does it matter for humans too?

Yes, but mildly — colocation is a common default in the Vitest/Vite world for the ordinary reasons (shorter import paths, tests as living documentation next to the thing they test, less friction to write the test). For a human, a mirrored `tests/` dir is navigable; it's a preference, not a real cost. The AI-editing angle is what turns a preference into a recommendation.

## The one real objection, and how to handle it

The usual case *for* a separate `tests/` tree is keeping test noise out of `src/` — cleaner file listings, easy to exclude from builds, clear separation. Both concerns are solvable without giving up colocation:

- **Build/bundle exclusion:** the `.test.tsx` suffix already handles this. Vitest picks up `*.test.*` by default; your bundler and `tsconfig`/build globs exclude the same pattern. No directory boundary needed.
- **Listing noise:** real, but modest, and worth it for the agent benefit. If a particular module has heavy fixtures or large integration suites, those are the exception — park *those* in a local `__tests__/` folder or a top-level `tests/` for true end-to-end suites. Unit tests stay colocated.

## Recommendation

- Colocate unit/component tests: `Foo.test.tsx` next to `Foo.tsx`.
- Keep a top-level `tests/` (or `e2e/`) only for genuinely cross-cutting integration/e2e suites that don't belong to a single source file.
- Migrate incrementally — move tests as you touch each area rather than in one big sweep; update the Vitest `include` glob to `src/**/*.test.{ts,tsx}` (plus your e2e dir) and you're done.

The deciding factor isn't dogma about separation of concerns — it's that an agent acts on what's in the open file's neighbourhood, and colocation puts the test in that neighbourhood.

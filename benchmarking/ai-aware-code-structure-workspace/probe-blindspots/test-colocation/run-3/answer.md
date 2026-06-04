# Where should the test files live?

Colocate them. Move from `tests/` mirroring `src/` to `Foo.test.tsx` sitting beside `Foo.tsx`. The choice does matter, and it matters more now that Claude Code is your main editor.

## Why it matters more with an agent

The deciding factor is how AI coding agents behave: they are reluctant to look at files that aren't already in front of them. Getting an agent to proactively open a sibling file is like pulling teeth. It works with the open file and makes confident changes.

A mirrored `tests/` tree puts maximum distance between a unit and its test. When the agent is editing `src/checkout/Foo.tsx`, the test sits at `tests/checkout/Foo.test.tsx` — a different subtree it has to think to go find. In practice that means:

- It edits `Foo.tsx` and never updates (or even reads) the test, so coverage silently rots.
- It writes a *new* test from scratch instead of extending the existing one, because it didn't see that one already exists.
- It can't use the existing test as context for how `Foo` is meant to behave — which is some of the highest-signal documentation you have.

Colocation puts the test directly adjacent to the source. When the agent opens `Foo.tsx`, `Foo.test.tsx` is right there in the same directory listing, named the same, impossible to miss. You get the test pulled into context for free, exactly when it's relevant. That's the single highest-value move here: it removes a cross-file lookup the agent is most likely to skip.

This also lines up with your TDD preference. If tests are meant to be written alongside implementation, they should physically sit alongside it. A mirrored tree quietly works against that habit for both you and the agent.

## The case for `tests/` — and why it's weak here

The usual arguments for a separate tree:

- **Keeps `src/` "clean."** Real but cosmetic. A `.test.tsx` next to a `.tsx` is obvious and easy to filter (`**/*.test.*`) in your editor, in coverage config, and in build excludes. Vitest already handles this — `include`/`exclude` globs don't care where the files sit.
- **Easier to exclude from the bundle.** Already a solved problem regardless of location: test files are excluded by glob, not by directory. Vitest and your bundler match `*.test.*` wherever it lives.
- **Mirrors src/ so things are "findable."** This is the trap. A mirror is only findable if you (or the agent) reliably translate one path into the other. Colocation removes the translation entirely — the test is *at* the source.

None of these outweigh the context win for an agent-driven workflow.

## Practical notes

- **Unit/component tests:** colocate. `Foo.tsx` ↔ `Foo.test.tsx`.
- **Integration / e2e / cross-cutting tests** that don't belong to a single source file: those legitimately have no "beside" to sit next to. Keep a small top-level `tests/` (or `e2e/`) for them. So it's not strictly either/or — colocate the unit tests, keep a thin top-level dir for the genuinely cross-cutting ones.
- **Shared fixtures/helpers** can live in a `test/` or `__fixtures__/` folder; colocation is about the tests that map 1:1 to a unit, not every test artifact.
- Vitest config stays trivial: `include: ['src/**/*.test.{ts,tsx}']` plus whatever top-level e2e glob you keep.

## Migration

It's a mechanical move — shift each `tests/foo/Bar.test.tsx` next to its `src/foo/Bar.tsx` and fix the relative imports (they usually get *shorter*, often `./Bar` instead of `../../src/foo/Bar`, which is another small readability win). Worth doing in one pass so you don't end up with a confusing hybrid where some tests are colocated and some aren't. Update the Vitest `include`/`coverage` globs in the same change.

## Bottom line

Colocate. With Claude Code as the primary editor, putting the test beside the source means it lands in context exactly when the agent touches the code — which is the difference between tests that stay in sync and tests that quietly drift. Keep a thin top-level dir only for cross-cutting tests that have no single home.

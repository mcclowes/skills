---
name: code-frontmatter
description: 'Context-efficient codebase navigation and documentation using structured frontmatter headers. Use this when exploring an unfamiliar codebase, answering "where is X / how does Y work" questions, or when asked to add/maintain file-level documentation. Index a tree''s headers in one pass instead of reading every file, and generate or validate frontmatter with the bundled scripts. Reach for it whenever token budget matters while navigating code, even if the user does not say "frontmatter".'
---

# Code Frontmatter

A frontmatter block is a short YAML header in a comment at the top of a source file describing its **purpose** and its **related** files. The point is leverage: a 300-line file's header costs ~50 tokens to read instead of ~1500 for the whole file, so you can map a codebase from headers and only open the files that actually matter.

There are two modes, and a codebase has to be in the first before the second pays off:

- **Authoring** — adding frontmatter to files that lack it. This is where the work is, and the bundled `generate` script does the mechanical part.
- **Navigating** — reading headers (not whole files) to build a mental map. This is the payoff, and the `index` script does it in a single pass.

Don't read the example files or `SPECIFICATION.md` unless you need the full schema — this file is enough for the common case.

## The scripts do the heavy lifting

`scripts/frontmatter.py` is stdlib-only (no install). Prefer it over doing this by hand — one script call beats N file reads.

```bash
# Navigate: print every documented file's purpose + related, in ONE pass.
# Also lists substantive files that are missing frontmatter (coverage gap).
python scripts/frontmatter.py index <dir> [--format md|json] [--min-lines N]

# Author: emit a skeleton header (purpose: TODO + related seeded from imports).
# --write inserts it in place (after any shebang); omit to print to stdout.
python scripts/frontmatter.py generate <file> [--write]

# Maintain: check frontmatter parses, has a purpose, and `related` paths resolve.
python scripts/frontmatter.py validate <dir>   # exit 1 if any issue
```

Adjust the path to wherever the skill lives. If Python isn't available, the manual workflows below still apply.

## Navigating a codebase

1. **Index the headers in one pass.** Run `index <dir>`. You get every file's purpose and related links plus a list of substantive files lacking headers — far cheaper than reading files one by one.

2. **If there are no scripts available**, batch-read headers instead of opening whole files. One `Grep` for `purpose:` across the tree surfaces every header at once:

   ```
   Grep  pattern="^\s*[#*/!-]*\s*purpose:"  output_mode="content"  -n=true  glob="*.{ts,py,go,rs}"
   ```

   For a single file, `Read` it with `limit: 20` to see only the header.

3. **Build the map, then load selectively.** From purposes and `related` links, decide which files are relevant. Only open a full file when you'll modify it or genuinely need its implementation. Follow `related` to discover connected files without loading them.

4. **No frontmatter? Say so and fall back.** If the codebase has little or no frontmatter, this skill's navigation benefit is limited — read files directly, and offer to add frontmatter (authoring mode) if the user will revisit this code.

## Authoring frontmatter

When asked to document files, or when you notice a codebase would benefit:

1. **Generate skeletons.** Run `generate <file>` per file (or loop over a directory). It pre-fills `related` from the file's internal imports and leaves `purpose` as a TODO — you fill in the judgment calls.

2. **Write a purpose that earns its tokens.** State what the file *does* and why someone would open it — not a restatement of the filename. "Genetic algorithm for FPL squad optimisation" beats "GA module". Trim `related` to the files a reader would actually jump to.

3. **Validate before you finish.** Run `validate <dir>`; fix any unresolved `related` paths or empty purposes.

4. **Be selective about what gets a header.** Frontmatter is an index, not blanket documentation. Add it to files that carry responsibility someone would search for. Skip: files under ~30 lines, test files, index/barrel files (unless re-exports are non-obvious), and config files.

## The schema

Two fields carry almost all the value. Everything else is optional and usually better expressed elsewhere (types, git history) — add it only when it genuinely aids navigation.

| Field     | Status      | Description                                                        |
| --------- | ----------- | ------------------------------------------------------------------ |
| `purpose` | **required** | One line: what the file does and why you'd open it (≤120 chars).   |
| `related` | recommended | Connected files as `path - reason`. The most valuable nav field.   |
| `inputs`  | optional    | Key parameters/data the file expects, as `name: type - desc`.      |
| `outputs` | optional    | Main return values/side effects, as `name: type - desc`.           |
| `note`    | optional    | Non-obvious context (e.g. naming history, gotchas).                |

Avoid `dependencies` (imports already say this), `exports` (types/`export` already say this), `usage` (prefer a doctest/JSDoc `@example`), and `modified` (git history is authoritative and never goes stale). Stale frontmatter is worse than none — it lies confidently — so document only what the header can keep true.

### Comment syntax by language

The block is always delimited by `---` lines inside the file's leading comment. `generate` produces the right wrapper automatically; these are for reference.

```python
"""
---
purpose: Brief description
related:
  - ./other.py - relationship
---
"""
```
```typescript
/**
 * ---
 * purpose: Brief description
 * related:
 *   - ./other.ts - relationship
 * ---
 */
```
```go
/*
---
purpose: Brief description
---
*/
```
```rust
//! ---
//! purpose: Brief description
//! ---
```

Ruby, shell, and YAML use `#`-prefixed lines (after any shebang). See `SPECIFICATION.md` for the complete per-language reference and the full optional-field list.

## Why this works

- **Token efficiency** — the whole point. Headers cost ~3% of the file; you spend the saved budget on actual work.
- **Better load decisions** — you know what a file is before committing context to it.
- **Doubles as human docs** — the header that helps you navigate also orients a new developer.

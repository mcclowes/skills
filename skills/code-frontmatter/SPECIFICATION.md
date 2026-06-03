# Code Frontmatter Specification

**Version**: 0.1.0  
**Status**: Draft

## Abstract

This specification defines a structured metadata format for source code files. The frontmatter block provides machine-readable context about a file's purpose, interface, and relationships without requiring the full file to be parsed.

## Motivation

AI coding assistants consume tokens proportional to the content they read. Loading a 300-line file to discover it implements "a genetic algorithm for team selection" wastes context window space that could be used for actual work.

By standardising a frontmatter format, tools can:

- Index codebases efficiently
- Make informed decisions about which files to load
- Understand file relationships without parsing imports
- Provide better navigation and documentation

## Specification

### Location

Frontmatter MUST appear at the very beginning of a file, within the first comment block.

### Delimiters

The frontmatter block MUST be delimited by `---` markers on their own lines within the comment.

### Format

The content between delimiters MUST be valid YAML.

> **Core schema.** In practice only two fields carry the navigation value: `purpose` (required)
> and `related` (recommended). Everything below is permitted by this spec but should be used
> sparingly — most of it is better expressed elsewhere (see "Discouraged fields"). `SKILL.md`
> is the day-to-day guidance; this document is the exhaustive reference.

### Required Fields

| Field     | Type   | Description                                                             |
| --------- | ------ | ----------------------------------------------------------------------- |
| `purpose` | string | A concise description of what the file does (max 120 chars recommended) |

### Recommended Fields

| Field     | Type | Description                                                          |
| --------- | ---- | -------------------------------------------------------------------- |
| `related` | list | Connected files as `path - reason`. The highest-value nav field.     |

### Optional Fields

| Field     | Type   | Description                                            |
| --------- | ------ | ------------------------------------------------------ |
| `inputs`  | list   | Parameters, arguments, or data the file/module expects |
| `outputs` | list   | Return values, side effects, or data produced          |
| `note`    | string | Non-obvious context (naming history, gotchas)          |
| `tags`    | list   | Categorical labels for filtering                       |
| `status`  | string | `stable`, `experimental`, `deprecated`                 |

### Discouraged fields

These are valid YAML but tend to go stale or duplicate information the language already
carries. Prefer the alternative:

| Field          | Prefer instead                                             |
| -------------- | ---------------------------------------------------------- |
| `dependencies` | the file's own `import`/`require` statements               |
| `exports`      | the language's `export`/`pub`/public symbols and types     |
| `usage`        | a doctest or JSDoc `@example` that stays runnable           |
| `modified`     | git history (authoritative, never drifts)                  |

Stale frontmatter is worse than none — it misleads with confidence. Only record what the
header can realistically be kept true.

### Input/Output Format

Each input or output entry SHOULD follow the pattern:

```
- name: type - description
```

Example:

```yaml
inputs:
  - players: list[Player] - available player pool
  - budget: float - maximum spend allowed
outputs:
  - team: list[Player] - optimal 15-player squad
  - score: float - predicted points
```

### Dependency Format

Dependencies SHOULD use:

- Package names for external dependencies
- Relative paths (starting with `./` or `../`) for internal files

Example:

```yaml
dependencies:
  - numpy
  - pandas
  - ./utils/scoring.py
  - ../config.py
```

### Related Files Format

Each related entry SHOULD include the path and relationship:

```yaml
related:
  - ./cache.py - provides caching layer used by this fetcher
  - ./models.py - defines data structures returned
```

## Language-Specific Syntax

### Python

```python
"""
---
purpose: Description here
---
"""
```

### JavaScript/TypeScript

```javascript
/**
 * ---
 * purpose: Description here
 * ---
 */
```

### Go

```go
/*
---
purpose: Description here
---
*/
```

### Rust

```rust
//! ---
//! purpose: Description here
//! ---
```

### Ruby

```ruby
# ---
# purpose: Description here
# ---
```

### Shell/Bash

```bash
# ---
# purpose: Description here
# ---
```

After the shebang if present:

```bash
#!/bin/bash
# ---
# purpose: Description here
# ---
```

## Parsing Rules

1. Read the first 30 lines of the file (configurable)
2. Identify the comment syntax for the file type
3. Locate `---` delimiters within comment blocks
4. Extract content between delimiters
5. Strip comment prefixes (e.g., `#`, `*`, `//!`)
6. Parse as YAML

## Example

Recommended shape — `purpose` + `related`, with `inputs`/`outputs` only where they aid a caller:

```python
"""
---
purpose: Genetic algorithm for Fantasy Premier League team optimisation
inputs:
  - players: list[Player] - all available players with stats
  - budget: float - maximum team cost (default 100.0)
outputs:
  - team: list[Player] - optimal 15-player squad
  - fitness: float - predicted total points
related:
  - ./fitness.py - fitness function implementation
  - ./selection.py - player selection strategies
---
"""

import numpy as np
from .player import Player
from .fitness import calculate_fitness

# ... rest of implementation
```

Note what is *absent*: `dependencies` (the imports below already say it), `exports` (Python's
public symbols say it), `usage` (a doctest stays runnable), and `modified` (git knows). Adding
them creates four more things that can drift out of sync with the code.

## Tooling

These three tools ship with the skill as subcommands of `scripts/frontmatter.py`
(stdlib-only, no install):

### Indexer — `index`

Scans a directory and emits every file's frontmatter in one pass, plus the files that
lack it. `--format json` produces:

```json
{
  "files": [
    {
      "path": "src/ga.py",
      "purpose": "Genetic algorithm for FPL team optimisation",
      "related": ["./fitness.py - fitness function implementation"]
    }
  ],
  "missing_frontmatter": ["src/legacy.py"],
  "coverage": "1/2"
}
```

### Validator — `validate`

Checks that frontmatter parses, `purpose` is present and non-empty, and every `related`
path resolves on disk (extension-optional). Exits non-zero when any issue is found, so it
drops straight into a pre-commit hook or CI step.

### Generator — `generate`

Creates skeleton frontmatter for a file by detecting its internal (relative/aliased)
imports and seeding the `related` list from them, leaving `purpose` as a TODO for human
or model judgement. `--write` inserts the block in place, after any shebang.

## Versioning

This specification follows Semantic Versioning. The version is indicated in the document header.

## License

This specification is released under CC0 1.0 Universal (Public Domain).

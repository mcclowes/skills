#!/usr/bin/env python3
"""
---
purpose: CLI for code-frontmatter — index, validate, and generate frontmatter across a codebase
related:
  - ../SKILL.md - the skill that invokes this tool
  - ../SPECIFICATION.md - the frontmatter schema this implements
---

Stdlib-only (no PyYAML). One tool, three subcommands:

  index     Scan a tree and print every file's frontmatter in ONE pass (the navigation payoff).
  validate  Check frontmatter is well-formed, required fields present, and `related` paths resolve.
  generate  Emit a skeleton frontmatter block for a file (purpose: TODO + related seeded from imports).

Run `python frontmatter.py <subcommand> --help` for details.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Language / comment-syntax knowledge
# ---------------------------------------------------------------------------

# Map extension -> how a frontmatter block is wrapped + the per-line prefix to strip.
# We keep this small and generic; the block is always delimited by `---` lines.
LANGS = {
    ".py":   {"open": '"""',   "close": '"""',  "prefix": "",    "line": "{}"},
    ".js":   {"open": "/**",   "close": " */",  "prefix": "* ",  "line": " * {}"},
    ".jsx":  {"open": "/**",   "close": " */",  "prefix": "* ",  "line": " * {}"},
    ".ts":   {"open": "/**",   "close": " */",  "prefix": "* ",  "line": " * {}"},
    ".tsx":  {"open": "/**",   "close": " */",  "prefix": "* ",  "line": " * {}"},
    ".mjs":  {"open": "/**",   "close": " */",  "prefix": "* ",  "line": " * {}"},
    ".go":   {"open": "/*",    "close": "*/",   "prefix": "",    "line": "{}"},
    ".rs":   {"open": "",      "close": "",     "prefix": "//! ", "line": "//! {}"},
    ".rb":   {"open": "",      "close": "",     "prefix": "# ",  "line": "# {}"},
    ".sh":   {"open": "",      "close": "",     "prefix": "# ",  "line": "# {}"},
    ".bash": {"open": "",      "close": "",     "prefix": "# ",  "line": "# {}"},
    ".yml":  {"open": "",      "close": "",     "prefix": "# ",  "line": "# {}"},
    ".yaml": {"open": "",      "close": "",     "prefix": "# ",  "line": "# {}"},
}

IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build", "__pycache__", "venv", ".venv",
    ".next", "out", "target", "coverage", ".turbo", ".cache", "vendor",
}

# Comment-prefix tokens we strip from any line when hunting for the `---` block.
# Generic across languages so we don't need perfect per-language parsing.
_PREFIX_RE = re.compile(r"^\s*(?:///|//!|//|\*/|\*|#+|\"\"\"|'''|/\*)?\s?")


@dataclass
class Frontmatter:
    path: str
    purpose: str | None = None
    related: list[str] = field(default_factory=list)
    raw: dict[str, object] = field(default_factory=dict)
    start_line: int = 0
    end_line: int = 0
    error: str | None = None


def _strip_prefix(line: str) -> str:
    """Remove a leading comment token + one space, language-agnostically."""
    return _PREFIX_RE.sub("", line, count=1).rstrip("\n")


def extract_block(path: str, max_lines: int = 60) -> tuple[list[str], int, int] | None:
    """Return (yaml_lines, start_lineno, end_lineno) for the frontmatter, or None."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            head = [next(fh) for _ in range(max_lines)]
    except (OSError, StopIteration) as e:
        if isinstance(e, StopIteration):
            # File shorter than max_lines — re-read fully.
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                head = fh.readlines()
        else:
            return None

    start = None
    body: list[str] = []
    for i, raw in enumerate(head, start=1):
        stripped = _strip_prefix(raw)
        if start is None:
            if stripped == "---":
                start = i
            continue
        if stripped == "---":
            return body, start, i
        body.append(stripped)
    return None


# ---------------------------------------------------------------------------
# Minimal YAML-subset parser (purpose scalar + simple list fields)
# Good enough for frontmatter; avoids a PyYAML dependency.
# ---------------------------------------------------------------------------

def parse_frontmatter(path: str) -> Frontmatter | None:
    extracted = extract_block(path)
    if extracted is None:
        return None
    body, start, end = extracted
    fm = Frontmatter(path=path, start_line=start, end_line=end)

    current_key: str | None = None
    for line in body:
        if not line.strip():
            continue
        # List item under the current key, e.g. "  - ./foo - reason"
        m = re.match(r"^\s*-\s+(.*)$", line)
        if m and current_key:
            fm.raw.setdefault(current_key, [])
            if isinstance(fm.raw[current_key], list):
                fm.raw[current_key].append(m.group(1).strip())  # type: ignore[union-attr]
            continue
        # key: value  (value may be empty -> list/block follows)
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            current_key = key
            if val and val not in ("|", ">"):
                fm.raw[key] = val.strip("'\"")
            else:
                fm.raw[key] = "" if val in ("|", ">") else []
            continue
        # Continuation of a literal block (usage: |) — append to scalar.
        if current_key and isinstance(fm.raw.get(current_key), str):
            fm.raw[current_key] = (fm.raw[current_key] + "\n" + line.strip()).strip()

    purpose = fm.raw.get("purpose")
    fm.purpose = purpose if isinstance(purpose, str) else None
    rel = fm.raw.get("related")
    fm.related = rel if isinstance(rel, list) else []
    return fm


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def iter_source_files(root: str):
    if os.path.isfile(root):
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for name in sorted(filenames):
            ext = os.path.splitext(name)[1]
            if ext in LANGS:
                yield os.path.join(dirpath, name)


# ---------------------------------------------------------------------------
# Subcommand: index
# ---------------------------------------------------------------------------

def cmd_index(args) -> int:
    root = args.path
    indexed: list[Frontmatter] = []
    missing: list[str] = []
    for path in iter_source_files(root):
        fm = parse_frontmatter(path)
        if fm and fm.purpose:
            indexed.append(fm)
        else:
            # Only flag substantive files as "missing" frontmatter.
            try:
                nlines = sum(1 for _ in open(path, "r", encoding="utf-8", errors="replace"))
            except OSError:
                nlines = 0
            if nlines >= args.min_lines:
                missing.append(path)

    rel = lambda p: os.path.relpath(p, root if os.path.isdir(root) else os.path.dirname(root))

    if args.format == "json":
        import json
        payload = {
            "files": [
                {"path": rel(fm.path), "purpose": fm.purpose, "related": fm.related}
                for fm in indexed
            ],
            "missing_frontmatter": [rel(p) for p in missing],
            "coverage": f"{len(indexed)}/{len(indexed) + len(missing)}",
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"# Frontmatter index — {len(indexed)} documented, {len(missing)} missing\n")
        for fm in indexed:
            print(f"## {rel(fm.path)}")
            print(f"{fm.purpose}")
            if fm.related:
                for r in fm.related:
                    print(f"  → {r}")
            print()
        if missing:
            print("## Files lacking frontmatter (≥%d lines)" % args.min_lines)
            for p in missing:
                print(f"  - {rel(p)}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: validate
# ---------------------------------------------------------------------------

def cmd_validate(args) -> int:
    root = args.path
    errors: list[str] = []
    checked = 0
    for path in iter_source_files(root):
        fm = parse_frontmatter(path)
        if fm is None:
            continue
        checked += 1
        if not fm.purpose:
            errors.append(f"{path}:{fm.start_line}: missing or empty `purpose`")
        base = os.path.dirname(path)
        for entry in fm.related:
            # entry looks like "./foo.ts - reason" — take the path token.
            token = entry.split()[0] if entry else ""
            if token.startswith((".", "/")):
                target = os.path.normpath(os.path.join(base, token))
                # Allow bare path or path with an extension already present.
                if not (os.path.exists(target) or _resolves_loosely(target)):
                    errors.append(
                        f"{path}:{fm.start_line}: `related` path does not resolve: {token}"
                    )
    if errors:
        print(f"✗ {len(errors)} issue(s) across {checked} file(s) with frontmatter:\n")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"✓ {checked} file(s) with frontmatter validated, no issues")
    return 0


def _resolves_loosely(target: str) -> bool:
    """A `related` path may omit the extension (e.g. './client')."""
    if os.path.exists(target):
        return True
    parent = os.path.dirname(target)
    stem = os.path.basename(target)
    if not os.path.isdir(parent):
        return False
    for name in os.listdir(parent):
        if name == stem or name.startswith(stem + "."):
            return True
    return False


# ---------------------------------------------------------------------------
# Subcommand: generate
# ---------------------------------------------------------------------------

IMPORT_PATTERNS = [
    re.compile(r"""^\s*from\s+['"]?([^'";\s]+)['"]?\s+import""", re.M),      # py
    re.compile(r"""^\s*import\s+['"]?([^'";\s]+)['"]?""", re.M),             # py
    re.compile(r"""import\s+(?:[^'"]*\s+from\s+)?['"]([^'"]+)['"]""", re.M), # js/ts
    re.compile(r"""require\(['"]([^'"]+)['"]\)""", re.M),                    # js
]


def _detect_internal_imports(path: str) -> list[str]:
    try:
        text = open(path, "r", encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    found: list[str] = []
    for pat in IMPORT_PATTERNS:
        for m in pat.findall(text):
            if m.startswith((".", "..", "@/", "@@/")):
                if m not in found:
                    found.append(m)
    return found


def cmd_generate(args) -> int:
    path = args.path
    ext = os.path.splitext(path)[1]
    lang = LANGS.get(ext)
    if not lang:
        print(f"Unsupported file type: {ext}", file=sys.stderr)
        return 2

    if parse_frontmatter(path) and not args.force:
        print(f"{path} already has frontmatter (use --force to print a fresh skeleton anyway)",
              file=sys.stderr)
        return 1

    internal = _detect_internal_imports(path)
    yaml_lines = ["---", "purpose: TODO - one line on what this file does"]
    if internal:
        yaml_lines.append("related:")
        for imp in internal:
            yaml_lines.append(f"  - {imp} - TODO why this file relates")
    yaml_lines.append("---")

    rendered = _render_block(yaml_lines, lang)
    if args.write:
        _insert_block(path, rendered)
        print(f"Inserted skeleton frontmatter into {path}. Fill in the TODOs.")
    else:
        print(rendered)
    return 0


def _render_block(yaml_lines: list[str], lang: dict) -> str:
    out: list[str] = []
    if lang["open"]:
        out.append(lang["open"])
    for yl in yaml_lines:
        out.append(lang["line"].format(yl) if yl else lang["prefix"].rstrip())
    if lang["close"]:
        out.append(lang["close"])
    return "\n".join(out)


def _insert_block(path: str, block: str) -> None:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        content = fh.read()
    lines = content.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith("#!"):  # shebang
        insert_at = 1
    new = lines[:insert_at] + [block + "\n\n"] + lines[insert_at:]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("".join(new))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="code-frontmatter tooling")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("index", help="scan a tree and print all frontmatter in one pass")
    pi.add_argument("path", help="directory or file")
    pi.add_argument("--format", choices=["md", "json"], default="md")
    pi.add_argument("--min-lines", type=int, default=30,
                    help="only flag files >= this many lines as missing frontmatter")
    pi.set_defaults(func=cmd_index)

    pv = sub.add_parser("validate", help="check frontmatter well-formedness and related paths")
    pv.add_argument("path", help="directory or file")
    pv.set_defaults(func=cmd_validate)

    pg = sub.add_parser("generate", help="emit skeleton frontmatter for a file")
    pg.add_argument("path", help="file to generate frontmatter for")
    pg.add_argument("--write", action="store_true", help="insert into the file in place")
    pg.add_argument("--force", action="store_true", help="generate even if frontmatter exists")
    pg.set_defaults(func=cmd_generate)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

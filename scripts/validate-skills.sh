#!/usr/bin/env bash
#
# Validate every skills/*/SKILL.md against the constraints that the
# `npx skills` CLI (and the Claude skill spec) enforce. Skills that
# violate these are SILENTLY dropped from the install picker, so we
# fail loudly here instead.
#
# Checks:
#   - SKILL.md has a `name` field
#   - SKILL.md has a `description` field
#   - description is <= 1024 CHARACTERS (not bytes; em-dashes count as 1)
#   - description frontmatter is valid YAML (an unquoted plain scalar
#     containing ": " is parsed as a nested mapping and throws, which
#     makes `npx skills add` SILENTLY drop the skill)
#
# Used by both the pre-commit hook (.githooks/pre-commit) and CI
# (.github/workflows/validate-skills.yml).

set -euo pipefail

LIMIT=1024
fail=0
checked=0

# Resolve repo root so the script works from any CWD / from a git hook.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Character count (codepoints), identical on macOS and Linux.
charlen() {
  if command -v perl >/dev/null 2>&1; then
    printf '%s' "$1" | perl -CS -ne 'print length($_)'
  else
    # Fallback: strip UTF-8 continuation bytes, count the rest.
    printf '%s' "$1" | LC_ALL=C tr -d '\200-\277' | wc -c | tr -d ' '
  fi
}

# Pull a single-line frontmatter value (only within the first --- ... --- block).
frontmatter_value() {
  local file="$1" key="$2"
  awk -v key="$key" '
    /^---[[:space:]]*$/ { fm++; next }
    fm==1 && $0 ~ "^" key ":[[:space:]]" {
      sub("^" key ":[[:space:]]*", "")
      print
      exit
    }
    fm>=2 { exit }
  ' "$file"
}

shopt -s nullglob
for f in skills/*/SKILL.md; do
  checked=$((checked + 1))
  name="$(frontmatter_value "$f" name)"
  desc="$(frontmatter_value "$f" description)"

  if [ -z "$name" ]; then
    echo "FAIL $f: missing 'name' in frontmatter"
    fail=1
  fi

  if [ -z "$desc" ]; then
    echo "FAIL $f: missing 'description' in frontmatter"
    fail=1
    continue
  fi

  # YAML parseability: a plain (unquoted) scalar cannot contain ": " — YAML
  # reads it as a nested mapping and throws, and the CLI swallows the error.
  # Quoted ('...'/"...") and block (|/>) scalars are exempt.
  first_char="${desc:0:1}"
  case "$first_char" in
    "'"|'"'|'|'|'>') ;;  # quoted or block scalar — safe
    *)
      if printf '%s' "$desc" | grep -q ': '; then
        echo "FAIL $f: unquoted description contains ': ' — YAML misparses it and 'npx skills add' silently drops the skill. Wrap the description in single quotes."
        fail=1
      fi
      ;;
  esac

  len="$(charlen "$desc")"
  if [ "$len" -gt "$LIMIT" ]; then
    echo "FAIL $f: description is $len chars (limit $LIMIT) — it will be dropped by 'npx skills add'"
    fail=1
  else
    echo "ok   $f: ${len} chars"
  fi
done

if [ "$checked" -eq 0 ]; then
  echo "FAIL: no skills/*/SKILL.md files found (run from repo root)"
  exit 1
fi

if [ "$fail" -ne 0 ]; then
  echo
  echo "Skill validation failed. Trim the offending description(s) under ${LIMIT} characters."
  exit 1
fi

echo
echo "All ${checked} skill(s) valid."

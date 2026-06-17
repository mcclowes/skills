#!/usr/bin/env python3
"""Abstraction-level linter for pseudocode artifacts.

The thesis behind the pseudocode skill is that a *language-agnostic* plan is more
reviewable than prose precisely because it names the logic without collapsing into
code. If "pseudocode" silently becomes near-code, the artifact stops being a
verification surface and the whole premise evaporates. This linter is the
measurement instrument that catches that collapse.

It checks three things:
  1. Coverage   — does the artifact name all four required sections?
  2. Abstraction — is it free of target-language syntax and real API calls?
  3. Reviewability — is it short enough to scan in ~60 seconds?

Usage:
    python lint_pseudocode.py <artifact.md>            # human-readable report
    python lint_pseudocode.py <artifact.md> --json     # machine-readable

Exit code 0 if the artifact passes, 1 otherwise. Intended for both the skill
(self-check) and the benchmark harness (verifying arm B is genuinely pseudocode).
"""
import argparse
import json
import re
import sys

# Section coverage: each class of bug hides in a section, so missing one is a gap.
SECTION_PATTERNS = {
    "data_and_invariants": r"\b(data|invariant|shape|structure|state|field)s?\b",
    "control_flow": r"\b(flow|step|loop|for each|while|algorithm|recurse|iterate|then)\b",
    "edge_cases": r"\b(edge case|failure|empty|null|boundary|overflow|duplicate|single|illegal)\b",
    "interface_contract": r"\b(contract|input|output|return|throw|error|param|signature)s?\b",
}

# Real-code tells. These fire when the plan has stopped describing logic and started
# committing to a language. We look for syntax that pseudocode has no need for.
CODE_TELLS = [
    (r"=>", "arrow function (target-language syntax)"),
    (r"\bconst\s+\w+\s*=", "JS/TS `const` declaration"),
    (r"\blet\s+\w+\s*=", "JS/TS `let` declaration"),
    (r"\bdef\s+\w+\s*\(", "Python `def`"),
    (r"\bfunction\s+\w*\s*\(", "JS `function` keyword"),
    (r"\bpublic\s+(static\s+)?\w+\s+\w+\(", "Java/C# method signature"),
    (r"\.(map|filter|reduce|forEach|groupby|groupBy|sort)\s*\(", "stdlib method call"),
    (r"\bconsole\.(log|error)\s*\(", "console API call"),
    (r"\bprint\s*\(", "print() call"),
    (r"\bimport\s+\w+", "import statement"),
    (r"\breturn\s+\w+\.\w+\(", "method call in return"),
    (r"[;{}]\s*$", "trailing brace/semicolon (code structure)"),
    (r"\bnew\s+[A-Z]\w+\(", "constructor call"),
    (r"===|!==", "strict-equality operators"),
]

# Assignment/comparison arrows and words used by pseudocode are fine and expected:
# `←`, `<-`, "set X to Y", "if a < b". We do NOT flag those.

MAX_LINES = 60  # ~60-second review budget; longer means it collapsed into code.
MIN_NONBLANK = 4


def analyze(text: str) -> dict:
    lower = text.lower()
    lines = text.splitlines()
    nonblank = [ln for ln in lines if ln.strip()]
    # Strip fenced-code markers but keep content — pseudocode is often in a fence.
    body = "\n".join(ln for ln in lines if not ln.strip().startswith("```"))

    sections = {
        name: bool(re.search(pat, lower))
        for name, pat in SECTION_PATTERNS.items()
    }

    tells = []
    for i, ln in enumerate(body.splitlines(), 1):
        for pat, desc in CODE_TELLS:
            if re.search(pat, ln):
                tells.append({"line": i, "text": ln.strip()[:80], "reason": desc})

    sections_present = sum(sections.values())
    return {
        "sections": sections,
        "sections_present": sections_present,
        "sections_total": len(SECTION_PATTERNS),
        "code_tells": tells,
        "line_count": len(nonblank),
        "too_long": len(nonblank) > MAX_LINES,
        "too_short": len(nonblank) < MIN_NONBLANK,
    }


def verdict(a: dict) -> tuple[bool, list[str]]:
    problems = []
    missing = [k for k, v in a["sections"].items() if not v]
    if missing:
        problems.append(f"missing sections: {', '.join(missing)}")
    if a["code_tells"]:
        problems.append(
            f"{len(a['code_tells'])} code-collapse tell(s) — not language-agnostic"
        )
    if a["too_long"]:
        problems.append(
            f"{a['line_count']} lines (> {MAX_LINES}); not reviewable at a glance"
        )
    if a["too_short"]:
        problems.append(f"only {a['line_count']} lines; too thin to be a plan")
    return (len(problems) == 0, problems)


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint a pseudocode artifact.")
    ap.add_argument("path")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with open(args.path, encoding="utf-8") as f:
        text = f.read()

    a = analyze(text)
    ok, problems = verdict(a)

    if args.json:
        print(json.dumps({"passed": ok, "problems": problems, **a}, indent=2))
        return 0 if ok else 1

    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {args.path}")
    print(f"  sections: {a['sections_present']}/{a['sections_total']}  "
          f"lines: {a['line_count']}  code-tells: {len(a['code_tells'])}")
    for p in problems:
        print(f"  - {p}")
    for t in a["code_tells"][:10]:
        print(f"    L{t['line']}: {t['reason']}  ›  {t['text']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

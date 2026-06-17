#!/usr/bin/env python3
"""Grade a stdin/stdout solution program against a task's test cases.

LiveCodeBench problems are full programs: read stdin, print stdout. A task ships
public test cases (treated as the base / happy-path suite) and private test cases
(the plus / hidden-adversarial suite). A suite passes only if EVERY case matches
(stdout compared after stripping trailing whitespace per line).

Usage: python grade_stdio.py <task_json> <solution.py> [--timeout 10]
Outputs JSON: {"base_pass": bool, "plus_pass": bool, "base_detail": "...", ...}
"""
import argparse
import json
import subprocess
import sys


def norm(s):
    # Compare line-by-line, ignoring trailing whitespace and trailing blank lines.
    lines = [ln.rstrip() for ln in s.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def run_cases(sol_path, cases, timeout):
    """Return (all_passed, detail). Stops at first failure."""
    if not cases:
        return True, "no cases"
    for i, c in enumerate(cases):
        try:
            proc = subprocess.run(
                [sys.executable, sol_path],
                input=c["input"], capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return False, f"case {i}: timeout {timeout}s"
        if proc.returncode != 0:
            return False, f"case {i}: runtime error: {proc.stderr.strip()[-200:]}"
        if norm(proc.stdout) != norm(c["output"]):
            return False, (f"case {i}: wrong answer\n  in:  {c['input'][:80]!r}\n"
                           f"  exp: {norm(c['output'])[:80]!r}\n  got: {norm(proc.stdout)[:80]!r}")
    return True, f"{len(cases)}/{len(cases)} passed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_json")
    ap.add_argument("solution")
    ap.add_argument("--timeout", type=int, default=10)
    args = ap.parse_args()
    task = json.load(open(args.task_json))

    import os
    if not os.path.exists(args.solution):
        print(json.dumps({"task_id": task["task_id"], "base_pass": False,
                          "plus_pass": False, "missing": True}))
        return

    bp, bd = run_cases(args.solution, task["base_cases"], args.timeout)
    pp, pd = run_cases(args.solution, task["plus_cases"], args.timeout)
    print(json.dumps({"task_id": task["task_id"], "base_pass": bp, "plus_pass": pp,
                      "base_detail": bd, "plus_detail": pd, "missing": False}))


if __name__ == "__main__":
    main()

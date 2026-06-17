#!/usr/bin/env python3
"""Grade a solution file against a task's base and plus (edge) suites.

Runs each suite in a fresh subprocess with a timeout, so model-generated code
that hangs or crashes can't take down the harness. Reports pass/fail for each
suite separately — the base/plus split is the edge-case signal.

Usage:
    python grade.py <task_json> <solution.py> [--timeout 15]
Outputs JSON: {"base_pass": bool, "plus_pass": bool, "base_err": str, "plus_err": str}
"""
import argparse
import json
import subprocess
import sys
import tempfile
import os

RUNNER = '''
import sys
sys.setrecursionlimit(100000)
{solution}

{test}

try:
    check({entry_point})
    print("__PASS__")
except Exception as e:
    import traceback
    print("__FAIL__")
    traceback.print_exc()
'''


def run_suite(solution_src, test_src, entry_point, timeout):
    script = RUNNER.format(solution=solution_src, test=test_src, entry_point=entry_point)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(script)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=timeout,
        )
        out = proc.stdout + proc.stderr
        passed = "__PASS__" in proc.stdout
        err = "" if passed else out[-800:]
        return passed, err
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"
    finally:
        os.unlink(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_json")
    ap.add_argument("solution")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    task = json.load(open(args.task_json))
    solution_src = open(args.solution).read()

    base_pass, base_err = run_suite(
        solution_src, task["base_test"], task["entry_point"], args.timeout)
    plus_pass, plus_err = run_suite(
        solution_src, task["plus_test"], task["entry_point"], args.timeout)

    print(json.dumps({
        "task_id": task["task_id"],
        "base_pass": base_pass,
        "plus_pass": plus_pass,
        "base_err": base_err,
        "plus_err": plus_err,
    }))


if __name__ == "__main__":
    main()

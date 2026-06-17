#!/usr/bin/env python3
"""Grade every generated solution and aggregate the pilot into benchmark.json/md.

Walks <iteration>/<task_dir>/<arm>/run-<n>/solution.py, grades each against its
task's base (happy-path) and plus (edge-hardened) suites, lints arm-B pseudocode
artifacts, and reports per-arm / per-tier pass rates.

The load-bearing numbers:
  - Tier-H plus pass rate, arm B vs arm C  (pseudocode vs compute-matched prose)
  - Tier-H plus pass rate, arm B vs arm A  (pseudocode vs direct)
  - the edge gap (base minus plus) per arm  (where the thesis predicts B wins)
  - Tier-L, arm B vs A                       (control: skill should not help here)

Usage: python aggregate_pilot.py <iteration_dir> <corpus.json>
"""
import json
import os
import sys
import statistics
from grade import run_suite          # reuse the validated grader
import lint_pseudocode

ARMS = ["A_direct", "B_pseudocode", "C_prose"]
ARM_LABEL = {
    "A_direct": "A · direct",
    "B_pseudocode": "B · pseudocode",
    "C_prose": "C · prose-matched",
}
TIMEOUT = 15


def grade_solution(task, sol_path):
    if not os.path.exists(sol_path):
        return {"base_pass": False, "plus_pass": False, "missing": True}
    src = open(sol_path).read()
    bp, _ = run_suite(src, task["base_test"], task["entry_point"], TIMEOUT)
    pp, _ = run_suite(src, task["plus_test"], task["entry_point"], TIMEOUT)
    return {"base_pass": bp, "plus_pass": pp, "missing": False}


def lint_artifact(path):
    if not os.path.exists(path):
        return {"present": False, "passed": False}
    a = lint_pseudocode.analyze(open(path).read())
    ok, problems = lint_pseudocode.verdict(a)
    return {"present": True, "passed": ok, "sections": a["sections_present"],
            "code_tells": len(a["code_tells"]), "lines": a["line_count"],
            "problems": problems}


def wc(path):
    return len(open(path).read().split()) if os.path.exists(path) else 0


def main():
    it_dir, corpus_path = sys.argv[1], sys.argv[2]
    corpus = {t["task_id"]: t for t in json.load(open(corpus_path))}

    runs = []  # flat list of every graded run
    for task_id, task in corpus.items():
        tdir = task_id.replace("/", "__")
        for arm in ARMS:
            arm_dir = os.path.join(it_dir, tdir, arm)
            if not os.path.isdir(arm_dir):
                continue
            for run_name in sorted(os.listdir(arm_dir)):
                run_dir = os.path.join(arm_dir, run_name)
                if not os.path.isdir(run_dir):
                    continue
                g = grade_solution(task, os.path.join(run_dir, "solution.py"))
                rec = {"task_id": task_id, "tier": task["tier"], "arm": arm,
                       "run": run_name, **g}
                if arm == "B_pseudocode":
                    rec["lint"] = lint_artifact(os.path.join(run_dir, "pseudocode.md"))
                    rec["artifact_words"] = wc(os.path.join(run_dir, "pseudocode.md"))
                elif arm == "C_prose":
                    rec["artifact_words"] = wc(os.path.join(run_dir, "plan.md"))
                runs.append(rec)

    def rate(subset, key):
        vals = [1.0 if r[key] else 0.0 for r in subset]
        if not vals:
            return None, None, 0
        m = statistics.mean(vals)
        sd = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        return m, sd, len(vals)

    # per (arm, tier)
    summary = {}
    for arm in ARMS:
        for tier in ("H", "L"):
            sub = [r for r in runs if r["arm"] == arm and r["tier"] == tier]
            if not sub:
                continue
            bm, bsd, n = rate(sub, "base_pass")
            pm, psd, _ = rate(sub, "plus_pass")
            words = [r.get("artifact_words", 0) for r in sub if r.get("artifact_words")]
            summary[f"{arm}|{tier}"] = {
                "arm": arm, "tier": tier, "n": n,
                "base_pass": bm, "base_sd": bsd,
                "plus_pass": pm, "plus_sd": psd,
                "edge_gap": (bm - pm) if (bm is not None and pm is not None) else None,
                "mean_artifact_words": statistics.mean(words) if words else None,
                "missing": sum(1 for r in sub if r.get("missing")),
            }

    # arm-B lint health
    b_runs = [r for r in runs if r["arm"] == "B_pseudocode" and "lint" in r]
    lint_present = [r for r in b_runs if r["lint"]["present"]]
    lint_health = {
        "artifacts_present": len(lint_present),
        "of_total": len(b_runs),
        "lint_pass": sum(1 for r in lint_present if r["lint"]["passed"]),
        "mean_code_tells": (statistics.mean([r["lint"]["code_tells"] for r in lint_present])
                            if lint_present else None),
    }

    # per-task plus pass (to spot anchoring N2: B worse than A on a task)
    per_task = {}
    for task_id, task in corpus.items():
        row = {"tier": task["tier"]}
        for arm in ARMS:
            sub = [r for r in runs if r["task_id"] == task_id and r["arm"] == arm]
            m, _, n = rate(sub, "plus_pass")
            row[arm] = m
        per_task[task_id] = row

    benchmark = {
        "skill": "pseudocode",
        "iteration": os.path.basename(it_dir.rstrip("/")),
        "total_runs": len(runs),
        "summary": summary,
        "lint_health": lint_health,
        "per_task_plus_pass": per_task,
        "runs": runs,
    }
    json.dump(benchmark, open(os.path.join(it_dir, "benchmark.json"), "w"), indent=2)

    write_md(it_dir, benchmark)
    print("wrote benchmark.json and benchmark.md (", len(runs), "runs )")


def pct(x):
    return "—" if x is None else f"{round(x*100)}%"


def write_md(it_dir, b):
    s = b["summary"]
    L = []
    L.append(f"# Pseudocode benchmark — {b['iteration']}\n")
    L.append(f"Arms: **A** direct · **B** pseudocode-first · **C** prose-plan (compute-matched). "
             f"3 samples/task. {b['total_runs']} total runs.\n")
    L.append("Two suites per task: **base** (happy path) and **plus** (adversarial edge cases, "
             "from EvalPlus / hand-authored). The thesis predicts arm B's advantage shows up on "
             "the **plus** suite and on the **edge gap** (base − plus), concentrated in **Tier H**.\n")

    for tier, title in (("H", "Tier H — high logic complexity (the thesis tier)"),
                        ("L", "Tier L — trivial control (skill should NOT help)")):
        L.append(f"\n## {title}\n")
        L.append("| Arm | n | Base pass | Plus pass | Edge gap | Artifact words |")
        L.append("|---|---|---|---|---|---|")
        for arm in ARMS:
            row = s.get(f"{arm}|{tier}")
            if not row:
                continue
            words = "—" if row["mean_artifact_words"] is None else str(round(row["mean_artifact_words"]))
            L.append(f"| {ARM_LABEL[arm]} | {row['n']} | {pct(row['base_pass'])} "
                     f"| {pct(row['plus_pass'])} | {pct(row['edge_gap'])} | {words} |")

    # headline deltas on Tier H plus
    h = {arm: s.get(f"{arm}|H") for arm in ARMS}
    if all(h.values()):
        bA, bB, bC = h["A_direct"]["plus_pass"], h["B_pseudocode"]["plus_pass"], h["C_prose"]["plus_pass"]
        L.append("\n## Headline (Tier H, plus suite)\n")
        L.append(f"- **B vs A** (pseudocode vs direct): {pct(bB)} − {pct(bA)} = **{round((bB-bA)*100):+d} pts**")
        L.append(f"- **B vs C** (pseudocode vs compute-matched prose — the load-bearing test): "
                 f"{pct(bB)} − {pct(bC)} = **{round((bB-bC)*100):+d} pts**")
        L.append(f"- Artifact compute match: B ≈ {round(h['B_pseudocode']['mean_artifact_words'] or 0)} words "
                 f"vs C ≈ {round(h['C_prose']['mean_artifact_words'] or 0)} words")

    lh = b["lint_health"]
    L.append("\n## Arm-B artifact health (linter)\n")
    L.append(f"- pseudocode.md present: {lh['artifacts_present']}/{lh['of_total']}")
    L.append(f"- passes abstraction-level lint: {lh['lint_pass']}/{lh['artifacts_present']}")
    L.append(f"- mean code-tells (lower = more language-agnostic): "
             f"{round(lh['mean_code_tells'],2) if lh['mean_code_tells'] is not None else '—'}")

    # anchoring watch
    L.append("\n## Per-task plus pass (anchoring watch — B notably below A flags N2)\n")
    L.append("| Task | Tier | A | B | C |")
    L.append("|---|---|---|---|---|")
    for tid, row in b["per_task_plus_pass"].items():
        L.append(f"| {tid} | {row['tier']} | {pct(row['A_direct'])} "
                 f"| {pct(row['B_pseudocode'])} | {pct(row['C_prose'])} |")

    open(os.path.join(it_dir, "benchmark.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()

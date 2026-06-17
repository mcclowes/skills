#!/usr/bin/env python3
"""Grade + aggregate iteration 2, dispatching by task harness (functional | stdio).

Same arms (A/B/C) and same headline numbers as the pilot, but the corpus now
includes hard LiveCodeBench problems (stdio) that give arm A real headroom to
fall below ceiling — the condition under which B-vs-C can actually separate.

Usage: python aggregate_iter2.py <iteration_dir> <corpus_iter2.json>
"""
import json, os, sys, statistics
from concurrent.futures import ProcessPoolExecutor
from grade import run_suite                 # functional
from grade_stdio import run_cases           # stdio
import lint_pseudocode

ARMS = ["A_direct", "B_pseudocode", "C_prose"]
ARM_LABEL = {"A_direct": "A · direct", "B_pseudocode": "B · pseudocode",
             "C_prose": "C · prose-matched"}


STDIO_TIMEOUT = int(os.environ.get("STDIO_TIMEOUT", "10"))


def grade(task, sol_path):
    if not os.path.exists(sol_path):
        return {"base_pass": False, "plus_pass": False, "missing": True}
    if task["harness"] == "stdio":
        bp, _ = run_cases(sol_path, task["base_cases"], STDIO_TIMEOUT)
        pp, _ = run_cases(sol_path, task["plus_cases"], STDIO_TIMEOUT)
    else:
        src = open(sol_path).read()
        bp, _ = run_suite(src, task["base_test"], task["entry_point"], 15)
        pp, _ = run_suite(src, task["plus_test"], task["entry_point"], 15)
    return {"base_pass": bp, "plus_pass": pp, "missing": False}


def _grade_unit(args):
    """Top-level so it's picklable for the process pool."""
    task, sol_path, meta = args
    return {**meta, **grade(task, sol_path)}


def lint_artifact(path):
    if not os.path.exists(path):
        return {"present": False, "passed": False, "code_tells": None}
    a = lint_pseudocode.analyze(open(path).read())
    ok, _ = lint_pseudocode.verdict(a)
    return {"present": True, "passed": ok, "code_tells": len(a["code_tells"]),
            "sections": a["sections_present"]}


def wc(p):
    return len(open(p).read().split()) if os.path.exists(p) else 0


def rate(subset, key):
    vals = [1.0 if r[key] else 0.0 for r in subset]
    if not vals:
        return None, 0
    return statistics.mean(vals), len(vals)


def main():
    it_dir, corpus_path = sys.argv[1], sys.argv[2]
    corpus = {t["task_id"]: t for t in json.load(open(corpus_path))}
    # Build all grading units, then grade in parallel (each unit is independent).
    units = []
    for tid, task in corpus.items():
        tdir = tid.replace("/", "__")
        for arm in ARMS:
            adir = os.path.join(it_dir, tdir, arm)
            if not os.path.isdir(adir):
                continue
            for run_name in sorted(os.listdir(adir)):
                rdir = os.path.join(adir, run_name)
                if not os.path.isdir(rdir):
                    continue
                meta = {"task_id": tid, "tier": task["tier"], "source": task["source"],
                        "harness": task["harness"], "arm": arm, "run": run_name, "rdir": rdir}
                units.append((task, os.path.join(rdir, "solution.py"), meta))

    # CPU-bound timed solutions: oversubscribing workers causes wall-clock
    # contention and spurious TLEs, so default to serial. Override with WORKERS.
    workers = int(os.environ.get("WORKERS", "1"))
    print(f"grading {len(units)} runs, workers={workers}, stdio_timeout={STDIO_TIMEOUT}s ...", flush=True)
    if workers <= 1:
        graded = []
        for i, u in enumerate(units):
            graded.append(_grade_unit(u))
            if (i + 1) % 15 == 0:
                print(f"  graded {i+1}/{len(units)}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            graded = list(ex.map(_grade_unit, units))

    runs = []
    for rec in graded:
        rdir = rec.pop("rdir")
        if rec["arm"] == "B_pseudocode":
            rec["lint"] = lint_artifact(os.path.join(rdir, "pseudocode.md"))
            rec["artifact_words"] = wc(os.path.join(rdir, "pseudocode.md"))
        elif rec["arm"] == "C_prose":
            rec["artifact_words"] = wc(os.path.join(rdir, "plan.md"))
        runs.append(rec)

    # group by source bucket so LCB (headroom) and novel (control) are separate
    def summarize(subset_filter, label):
        block = {}
        for arm in ARMS:
            sub = [r for r in runs if r["arm"] == arm and subset_filter(r)]
            if not sub:
                continue
            bm, n = rate(sub, "base_pass")
            pm, _ = rate(sub, "plus_pass")
            words = [r.get("artifact_words", 0) for r in sub if r.get("artifact_words")]
            block[arm] = {"n": n, "base": bm, "plus": pm,
                          "edge_gap": (bm - pm) if bm is not None else None,
                          "words": statistics.mean(words) if words else None,
                          "missing": sum(1 for r in sub if r.get("missing"))}
        return {"label": label, "arms": block}

    buckets = {
        "lcb": summarize(lambda r: r["source"] == "livecodebench", "LiveCodeBench hard (stdio)"),
        "novel": summarize(lambda r: r["source"] == "novel", "Novel contamination-free (functional)"),
        "all": summarize(lambda r: True, "All tasks"),
    }

    b_runs = [r for r in runs if r["arm"] == "B_pseudocode" and "lint" in r]
    present = [r for r in b_runs if r["lint"]["present"]]
    lint_health = {
        "present": len(present), "of": len(b_runs),
        "lint_pass": sum(1 for r in present if r["lint"]["passed"]),
        "mean_code_tells": statistics.mean([r["lint"]["code_tells"] for r in present]) if present else None,
    }

    per_task = {}
    for tid, task in corpus.items():
        row = {"source": task["source"]}
        for arm in ARMS:
            sub = [r for r in runs if r["task_id"] == tid and r["arm"] == arm]
            m, _ = rate(sub, "plus_pass")
            row[arm] = m
        per_task[tid] = row

    bench = {"skill": "pseudocode", "iteration": os.path.basename(it_dir.rstrip("/")),
             "total_runs": len(runs), "buckets": buckets, "lint_health": lint_health,
             "per_task_plus_pass": per_task, "runs": runs}
    json.dump(bench, open(os.path.join(it_dir, "benchmark.json"), "w"), indent=2)
    write_md(it_dir, bench)
    print(f"wrote benchmark.json/md ({len(runs)} runs)")


def pct(x):
    return "—" if x is None else f"{round(x*100)}%"


def write_md(it_dir, b):
    L = [f"# Pseudocode benchmark — {b['iteration']}\n",
         "Arms: **A** direct · **B** pseudocode-first · **C** prose-plan (compute-matched). "
         "3 samples/task. " + str(b["total_runs"]) + " total runs.\n",
         "Base = happy/sample suite · Plus = hidden adversarial suite. The load-bearing test is "
         "**B vs C on Plus**: does *structure* beat *prose at equal compute*?\n"]
    for key in ("lcb", "novel", "all"):
        blk = b["buckets"][key]
        if not blk["arms"]:
            continue
        L.append(f"\n## {blk['label']}\n")
        L.append("| Arm | n | Base pass | Plus pass | Edge gap | Artifact words |")
        L.append("|---|---|---|---|---|---|")
        for arm in ARMS:
            a = blk["arms"].get(arm)
            if not a:
                continue
            w = "—" if a["words"] is None else str(round(a["words"]))
            L.append(f"| {ARM_LABEL[arm]} | {a['n']} | {pct(a['base'])} | {pct(a['plus'])} "
                     f"| {pct(a['edge_gap'])} | {w} |")
        arms = blk["arms"]
        if all(arm in arms for arm in ARMS):
            bA, bB, bC = arms["A_direct"]["plus"], arms["B_pseudocode"]["plus"], arms["C_prose"]["plus"]
            L.append(f"\n_Headline (Plus): **B−A = {round((bB-bA)*100):+d} pts**, "
                     f"**B−C = {round((bB-bC)*100):+d} pts** (load-bearing). "
                     f"Compute match: B≈{round(arms['B_pseudocode']['words'] or 0)}w vs "
                     f"C≈{round(arms['C_prose']['words'] or 0)}w._")
    lh = b["lint_health"]
    L.append("\n## Arm-B artifact health\n")
    L.append(f"- pseudocode.md present: {lh['present']}/{lh['of']} · "
             f"passes lint: {lh['lint_pass']}/{lh['present']} · "
             f"mean code-tells: {round(lh['mean_code_tells'],2) if lh['mean_code_tells'] is not None else '—'}")
    L.append("\n## Per-task Plus pass (anchoring watch — B << A flags N2)\n")
    L.append("| Task | Source | A | B | C |")
    L.append("|---|---|---|---|---|")
    for tid, row in b["per_task_plus_pass"].items():
        L.append(f"| {tid} | {row['source']} | {pct(row['A_direct'])} "
                 f"| {pct(row['B_pseudocode'])} | {pct(row['C_prose'])} |")
    open(os.path.join(it_dir, "benchmark.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()

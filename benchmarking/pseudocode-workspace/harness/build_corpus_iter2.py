#!/usr/bin/env python3
"""Assemble the iteration-2 corpus: hard LCB problems (stdio) + novel tasks (functional)."""
import json

lcb = {t["task_id"]: t for t in json.load(open("/tmp/corpus_lcb_all.json"))}

# Lean D/E (hard-but-doable); skip F (often floors all arms). Most-recent first.
SELECT = [
    "lcb/abc325_d", "lcb/abc325_e", "lcb/abc324_d", "lcb/abc324_e",
    "lcb/abc323_d", "lcb/abc323_e", "lcb/abc322_e", "lcb/abc320_e",
    "lcb/abc319_e", "lcb/abc318_e", "lcb/abc315_e",
]

corpus = []
for tid in SELECT:
    t = lcb[tid]
    t["harness"] = "stdio"
    corpus.append(t)

# Novel contamination-free tasks (functional harness), carried from iteration 1.
novel = json.load(open("/tmp/corpus_novel.json"))
for t in novel:
    t["harness"] = "functional"
    t["source"] = "novel"
    corpus.append(t)

WS = "/Users/mcclowes/Development/mcclowes/skills/benchmarking/pseudocode-workspace"
json.dump(corpus, open(f"{WS}/fixtures/corpus_iter2.json", "w"), indent=2)

from collections import Counter
print("iter2 tasks:", len(corpus),
      "harness:", dict(Counter(t["harness"] for t in corpus)),
      "source:", dict(Counter(t["source"] for t in corpus)))
for t in corpus:
    extra = (f"{len(t.get('base_cases',[]))}/{len(t.get('plus_cases',[]))} cases"
             if t["harness"] == "stdio" else "func")
    print(f"  {t['task_id']:26s} {t['harness']:10s} {extra}")

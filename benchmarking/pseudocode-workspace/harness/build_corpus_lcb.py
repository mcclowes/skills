#!/usr/bin/env python3
"""Build LCB corpus shard-by-shard to bound memory. Cap cases per problem."""
import json, glob, gc
import pyarrow.parquet as pq

MAX_BASE = 8       # public/sample cases as base suite
MAX_PLUS = 40      # cap hidden cases (some problems have thousands)
COLS = ["question_id", "difficulty", "contest_date", "platform",
        "question_content", "starter_code", "public_test_cases", "private_test_cases"]


def parse_cases(blob, cap):
    try:
        cases = json.loads(blob)
    except Exception:
        return None
    if not isinstance(cases, list) or not cases:
        return None
    out = []
    for c in cases:
        if c.get("testtype") != "stdin":
            return None
        out.append({"input": c["input"], "output": c["output"]})
        if len(out) >= cap:
            break
    return out


corpus = []
seen = set()
for f in sorted(glob.glob("/tmp/lcb_parquet/*.parquet")):
    pf = pq.ParquetFile(f)
    for batch in pf.iter_batches(batch_size=8, columns=COLS):
        for r in batch.to_pylist():
            if r["difficulty"] != "hard" or r["question_id"] in seen:
                continue
            base = parse_cases(r["public_test_cases"], MAX_BASE)
            plus = parse_cases(r["private_test_cases"], MAX_PLUS)
            if not base or not plus:
                continue
            seen.add(r["question_id"])
            corpus.append({
                "task_id": "lcb/" + r["question_id"],
                "tier": "H", "source": "livecodebench",
                "contest_date": str(r["contest_date"])[:10],
                "platform": r["platform"],
                "prompt": r["question_content"],
                "starter_code": r["starter_code"],
                "base_cases": base, "plus_cases": plus,
            })
        del batch; gc.collect()
    print(f"  scanned {f.split('/')[-1]}: corpus now {len(corpus)}")

corpus.sort(key=lambda c: c["contest_date"], reverse=True)
print(f"\nusable hard stdin problems: {len(corpus)}")
for c in corpus:
    print(f"  {c['task_id']:24s} {c['contest_date']} {c['platform']:9s} "
          f"base={len(c['base_cases'])} plus={len(c['plus_cases'])} promptlen={len(c['prompt'])}")
json.dump(corpus, open("/tmp/corpus_lcb_all.json", "w"))
print("wrote /tmp/corpus_lcb_all.json")

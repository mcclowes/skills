#!/usr/bin/env python3
"""Fetch HumanEval (base) + HumanEval+ (edge-hardened) and join into a corpus.

Per task we keep:
  prompt            - signature + docstring the agent implements
  entry_point       - function name
  base_test         - original HumanEval check() (functional / happy path)
  plus_test         - HumanEval+ check() (adds adversarial edge cases)

A solution that passes base_test but fails plus_test has an edge-case bug — that
gap is exactly the discriminating signal the pseudocode thesis predicts arm B
narrows. We grade base and plus separately.
"""
import json
import urllib.request

DSS = "https://datasets-server.huggingface.co/rows"

# Logic-heavy HumanEval problems (Tier H): subtle invariants, edge-case-rich,
# the kind where correct-looking code is routinely wrong. Plus a couple of
# trivial ones (Tier L) as the control that the skill should NOT help on.
SELECT = {
    # Tier H — high logic complexity
    "HumanEval/108": "H",  # count_nums: digit sum with negatives (signed first digit)
    "HumanEval/109": "H",  # move_one_ball: rotation-to-sorted feasibility
    "HumanEval/126": "H",  # is_sorted: sorted check with duplicate rule (famous edge)
    "HumanEval/129": "H",  # minPath: matrix neighbour BFS, lexicographic path
    "HumanEval/147": "H",  # get_max_triples: combinatorial mod counting
    "HumanEval/160": "H",  # do_algebra: operator-precedence expression build
    "HumanEval/100": "H",  # make_a_pile: parity-dependent step sequence
    "HumanEval/163": "H",  # generate_integers: even digits in range, order edge
    "HumanEval/115": "H",  # max_fill: grid bucket math with ceil
    # Tier L — trivial control (skill should add cost, not correctness)
    "HumanEval/23": "L",   # strlen
    "HumanEval/53": "L",   # add two numbers
}


def fetch_all(dataset, config="default"):
    rows = {}
    for offset in (0, 100):
        url = f"{DSS}?dataset={dataset}&config={config}&split=test&offset={offset}&length=100"
        with urllib.request.urlopen(url, timeout=60) as r:
            data = json.load(r)
        for item in data["rows"]:
            row = item["row"]
            rows[row["task_id"]] = row
    return rows


def main():
    print("fetching base (openai/openai_humaneval)…")
    base = fetch_all("openai/openai_humaneval", config="openai_humaneval")
    print("fetching plus (evalplus/humanevalplus)…")
    plus = fetch_all("evalplus/humanevalplus")

    corpus = []
    for tid, tier in SELECT.items():
        b = base.get(tid)
        p = plus.get(tid)
        if not b or not p:
            print(f"  MISSING {tid} (base={bool(b)} plus={bool(p)})")
            continue
        corpus.append({
            "task_id": tid,
            "tier": tier,
            "entry_point": b["entry_point"],
            "prompt": b["prompt"],
            "base_test": b["test"],          # original HumanEval check()
            "plus_test": p["test"],          # edge-hardened check()
            "_canonical": b["prompt"] + b["canonical_solution"],  # validation only
        })
    with open("/tmp/corpus_humaneval.json", "w") as f:
        json.dump(corpus, f, indent=2)
    print(f"wrote {len(corpus)} tasks to /tmp/corpus_humaneval.json")


if __name__ == "__main__":
    main()

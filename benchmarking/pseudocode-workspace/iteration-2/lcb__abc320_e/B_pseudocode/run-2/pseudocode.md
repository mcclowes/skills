# Flowing Noodles — plan

Verdict: invariant-heavy event scheduling with two interleaved priority queues. Plan first.

## Data & invariants
- `total[1..N]` : amount each person has received, init 0.
- `available` : min-heap of person ids currently in the row, keyed by id (front = smallest id).
  Invariant: contains exactly the people present in the row right now (relative to the event time being processed).
- `returning` : min-heap of (return_time, person_id) for people currently out of the row.
  Invariant: every person not in `available` is exactly once in `returning`.
  Global invariant: each person id appears in exactly one of the two structures at any moment.

Front of row = person with smallest id among those present (row order is by original number,
people only ever return to their original position, so the present person with smallest id is at front).

## Control flow
Events arrive sorted by T (guaranteed strictly increasing).
For each occurrence (T, W, S):
  1. Process returns: while `returning` non-empty AND its min return_time ≤ T:
        pop (rt, pid); push pid into `available`.
     (A person returning at time X is in the row at time X → use ≤ T, not < T.)
  2. If `available` non-empty:
        pid ← pop smallest id from `available`   # the front person
        total[pid] += W
        push (T + S, pid) into `returning`        # they leave, return at T+S
     else: noodles wasted, do nothing.
Output total[1..N], one per line.

## Edge cases & failure modes
- Empty row at an event (`available` empty after returns processed) → W discarded, no crash.
- Person returns at exactly T → counted as present (≤ comparison). Sample 1: person 1 returns at 4, event at 4 → gets the 100.
- Multiple people due back at/before same T → all reinserted before serving (while-loop drains all).
- Returns that happen after the last event → never reinserted, irrelevant to output (they got their noodles when served).
- N=1, repeated immediate returns (S small): person served, returns, served again — sample 3 sums all W = 15.
- Single event, W to front, rest get 0 → sample 2.
- Large values: T,S,W up to 1e9, M up to 2e5 → totals up to ~2e14, return times up to ~2e9; Python ints are unbounded, fine.

## Interface contract
- Input: N, M then M lines of T W S (T strictly increasing).
- Output: N lines, total[i].
- Initialization: at start all of 1..N are in `available`.
- Pure aside from building output; O((N+M) log N) via heaps.

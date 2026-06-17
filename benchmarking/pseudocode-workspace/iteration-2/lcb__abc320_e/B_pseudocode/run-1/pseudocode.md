# Flowing Noodles

Verdict: logic-heavy — two coordinated priority queues, time-ordered event
processing, with a subtle "returns are processed before the noodle drop at the
same time" ordering rule. Planning first.

## Data & invariants
- `available`: min-heap of person indices currently in the row (smallest index
  = front, since front = lowest-numbered present person; original positions are
  fixed so order in row is by index).
  - Invariant: every index in `available` is a person currently in the row and
    not currently stepped-out.
- `returning`: min-heap of (return_time, person_index) for people who stepped
  out and will come back.
  - Invariant: a person is in exactly one of {available, returning, currently
    front-eating-and-about-to-return} at any moment — never both.
- `total[i]`: accumulated noodles for person i. Can exceed 32-bit; use big ints
  (Python handles automatically).

## Control flow
Initialize available = all people 1..N (heapified), returning = empty,
total = all zeros.

For each event (T, W, S) in input order (T strictly increasing):
  1. Process returns: while returning non-empty AND its min return_time ≤ T:
       pop (rt, p); push p back into available.       # returns at time X count as present at X
  2. If available non-empty:
       p ← pop min from available                     # front of row
       total[p] += W
       push (T + S, p) into returning                 # steps out, comes back at T+S
     else: noodles wasted, do nothing.

(No need to process remaining returns after the loop — events are done.)

Loop boundaries: single pass over M events; inner while drains all returns due
by T. Each person pushed/popped from returning at most once per event served,
so total heap ops O(M log N) plus initial O(N).

## Edge cases & failure modes
- No one in row at event time → skip (sample 1, the 1e9 drop lands on empty row).
- Return time exactly equals an event time T → person IS available for that
  event: use `≤ T` in the while, and process returns BEFORE serving (step 1
  before step 2). This is the load-bearing ordering rule.
- Multiple returns due at same T → all reinstated before serving; heap order by
  index ensures correct front.
- A person could return and be served again in the same event (returns at T,
  then is front) — handled because step 1 precedes step 2.
- N people, M events independent; person may never be served → total stays 0
  (sample 2: people 2,3 → 0).
- Same person served repeatedly (N=1) → accumulates each time it's back in time
  (sample 3: person 1 always returns before next T since T increases by 1 and
  S grows, but actually must check availability) — heap logic handles naturally.
- Large values: W,S up to 1e9, sums up to 2e5*1e9 = 2e14 → needs 64-bit; Python
  ints are unbounded so safe.

## Interface contract
- Input: read N, M then M lines of T W S from stdin.
- Output: N lines, total[i] for i=1..N.
- Pure computation; no error cases for valid input per constraints.

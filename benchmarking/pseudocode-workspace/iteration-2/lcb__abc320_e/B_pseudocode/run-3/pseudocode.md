# Flowing Noodles — plan

## Data & invariants
- `totals[1..N]`: noodles each person has accumulated. Starts at 0.
- `available`: min-heap of person indices currently in the row, ordered by index
  (smallest index = front of row). Invariant: contains exactly the people present.
- `returning`: min-heap of (return_time, person_index) for people currently out.
  Invariant: a person is in exactly one of {available, returning, being-served-now}.
- Events come sorted by strictly increasing T_i (given).

## Control flow
Initialize available = all of 1..N (heap), returning = empty.

For each occurrence (T, W, S) in order of T:
  1. Process returns: while returning's smallest return_time <= T:
       pop (rt, p); push p into available.
     (People returning AT time T are present at time T → use <=.)
  2. If available non-empty:
       p = pop smallest index from available    # front person
       totals[p] += W
       push (T + S, p) into returning            # leaves now, back at T+S
     else: no one gets W (drop it).

After all occurrences, print totals[1..N].

## Why heaps are correct
- Front of row = smallest index present. A min-heap by index gives that in O(log N).
- Returns must be applied before serving the current event; ordering by return_time
  and draining all <= T restores everyone due by T.
- Since T strictly increases, a person served at T returns at T+S > T, so they cannot
  be re-served in the same step; the returning heap handles future steps.

## Edge cases & failure modes
- No one in row (available empty) at an event → noodles dropped, no change.
- Multiple returns at same time T → all drained in step 1 before serving.
- Person returns exactly at T → counted present (<= comparison). Matches sample 1
  (person 1 returns at time 4 and is served at time 4).
- Single person, repeated events where S keeps them out: sample 3 — person 1 served
  at t=1 (out until 2), present again at t=2, etc. Sums 1+2+...? Actually served when
  present: t=1 out till 2; t=2 present(returned at 2) served out till 4; t=3 absent;
  t=4 present served out till 8; t=5,6,7 absent; t=8 absent(returns at 8? out till 8
  means present at 8) — present at 8, served. Total = 1+2+4+8 = 15. Matches.
- Large values: W,S up to 1e9, T up to 1e9, N,M up to 2e5. totals can reach ~2e5*1e9
  = 2e14 → fits in 64-bit / Python int. return_time up to 2e9 → fine.

## Interface contract
- Read N, M then M lines of (T, W, S). Print N lines, total per person.
- Pure computation; output integers, no formatting.

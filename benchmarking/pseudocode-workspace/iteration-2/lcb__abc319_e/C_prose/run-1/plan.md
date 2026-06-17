# Plan

## Input/output contract
Read `N X Y` on the first line. Then read `N-1` lines, each giving `P_i T_i`
for the bus from stop `i` to stop `i+1`. Then read `Q` and `Q` query times
`q_i`. For each query, output one line: the earliest arrival time at Aoki's
house when leaving home at time `q_i`.

## Core observation
Every `P_i` lies in `[1, 8]`, so each waiting decision only depends on the
current time modulo `P_i`. The least common multiple of all integers from 1
to 8 is `LCM = 840`. If two journeys arrive at bus stop 1 at times that are
congruent modulo 840, then every subsequent bus wait is identical, and the
total time spent from stop 1 to stop N is the same. This lets us precompute,
for each residue `r` in `0..839`, the total travel time `f(r)` from arriving
at stop 1 at a time `t` with `t mod 840 == r` until arriving at stop N.

## Algorithm
1. For each residue `r` in `0..839`, simulate the chain of buses:
   - Start with `cur = r`.
   - For each `i` from `1` to `N-1`: wait until the next multiple of `P_i`,
     i.e. `cur = ceil(cur / P_i) * P_i`, then `cur += T_i`.
   - `f[r] = cur - r` is the elapsed time from stop 1 to stop N.
   This is `O(840 * N)` which is at most ~8.4e7 — acceptable.
2. For each query `q`:
   - Arrival at stop 1: `a = q + X`.
   - Total: `a + f[a mod 840] + Y`.

## Edge cases
- `N == 2`: no buses, `f` is computed with an empty loop so `f[r] = 0`; answer
  is `q + X + Y`.
- Already at a multiple of `P_i`: `ceil` keeps it (can board immediately).
- Large values up to 1e9 plus accumulation: Python big ints, no overflow.
- Fast IO via `sys.stdin` since `Q` can be 2e5.

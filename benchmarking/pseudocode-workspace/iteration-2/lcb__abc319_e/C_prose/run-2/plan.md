# Plan

## Input/output contract
Read `N X Y`, then `N-1` lines of `P_i T_i`, then `Q`, then `Q` query times `q_i`.
For each query, output on its own line the earliest arrival time at Aoki's house
when leaving home at time `q_i`.

## Core observation
The journey is deterministic forward simulation: from a current time `t`, walking
to stop 1 takes `X`; then for each stop `i` we wait for the next bus departure
(the smallest multiple of `P_i` that is `>= t`), ride it (`+T_i`) to reach stop
`i+1`; finally add `Y` to reach the destination.

The only place the *value* of `t` matters (beyond a constant offset) is the
waiting step, which depends on `t mod P_i`. Since every `P_i` is in `[1, 8]`, the
whole chain of waits depends only on `t mod L`, where `L = lcm(1..8) = 840`.
So if two start times have the same residue mod 840, their total added travel
time (everything after arriving at stop 1) is identical.

## Algorithm
1. Let `L = 840`. For each residue `r` in `0..L-1`, simulate the bus chain
   starting from time `r` (i.e. arrival-at-stop-1 time congruent to `r`):
   `cur = r`; for each `i`: `cur = ceil(cur / P_i) * P_i + T_i`. Store
   `delta[r] = cur - r` = total time from being at stop 1 (at a time ≡ r) until
   reaching stop N. This is O(L * N) ≈ 840 * 1e5 = 8.4e7, acceptable.
2. For a query `q`: arrival at stop 1 is `s = q + X`. Answer is
   `s + delta[s mod L] + Y`.

## Edge cases
- `ceil(cur / P) * P` handles "arrive exactly at departure" (remainder 0 -> wait 0).
- Large values fit in Python's arbitrary ints; no overflow.
- Use fast IO (sys.stdin buffer) for up to 2e5 queries.

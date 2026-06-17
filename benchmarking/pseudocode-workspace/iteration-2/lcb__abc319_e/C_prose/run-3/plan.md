# Plan

## Problem
Takahashi walks house -> stop 1 (X time), rides buses stop i -> i+1 (bus departs at
multiples of P_i, takes T_i time), then walks stop N -> Aoki (Y time). For each query
start time q, find earliest arrival at Aoki's house.

## Key observation
Each P_i is in [1, 8]. The least common multiple of {1,...,8} is L = 840. The waiting
behaviour at every bus stop depends only on the current time modulo P_i, hence only on
the current time modulo 840. Therefore the *total extra delay* incurred from the moment
you arrive at bus stop 1 onward is a function purely of (arrival_time_at_stop_1 mod 840).

So I precompute, for every residue r in [0, 840), the final arrival offset when you
arrive at bus stop 1 at a time t ≡ r (mod 840). Concretely, simulate the journey from
stop 1 to stop N starting at time r:
  cur = r
  for each i in 0..N-2:
      wait until next multiple of P_i: cur = ceil(cur / P_i) * P_i
      cur += T_i
  cur += Y   (final walk)
Store ans[r] = cur. The difference (ans[r] - r) is constant regardless of which actual
multiple-of-840 block we started in, because adding 840 to the start only shifts all the
"next multiple" computations by 840 too (840 is a multiple of every P_i).

## Per query
Arrival at stop 1 = q + X. Let t = q + X. The real answer = (t - (t mod 840)) + ans[t mod 840].
Because ans[r] was computed starting at the small value r, and the rest of the journey
adds the same amount; we add back the floor(t/840)*840 base block.

## Complexity
Precompute: 840 * N ~ 8.4e7 worst case — acceptable in optimized loops. Queries: O(Q).

## Edge cases
- N could be 2 (no buses if N-1=1? actually N>=2 means at least one bus when N>2; if N=2
  there is exactly one segment with P_1, T_1). Loop handles any count.
- Large values up to 1e9; use Python ints (arbitrary precision, no overflow).
- ceil division done via (cur + P - 1) // P * P.

## I/O contract
Read N X Y; then N-1 lines of P_i T_i; then Q; then Q query lines. Output Q lines,
each the earliest arrival time. Use fast input reading.

# Plan: Flowing Noodles

## Input/output contract
Read `N M` then `M` lines of `T_i W_i S_i`. The events are already sorted by strictly increasing `T_i`. Output `N` lines, the i-th being the total noodles person `i` received.

## Data structures
- `total[1..N]`: accumulated noodles per person (use plain ints; Python handles big ints).
- `available`: a min-heap of person indices that are currently in the row, ordered by index (smaller index = nearer the front). Initially holds `0..N-1` (0-based).
- `returning`: a min-heap of `(return_time, person_index)` for people who have stepped out and will rejoin at `return_time`.

## Algorithm
Process events in time order (they already are). For each event `(T, W, S)`:
1. Reinsert everyone whose `return_time <= T`: pop all entries from `returning` with `return_time <= T` and push their person index back onto `available`. A person returning exactly at time `X` counts as present at `X`, so the comparison is `<=`.
2. If `available` is non-empty, pop the smallest index `p` (front of row). Add `W` to `total[p]`. Schedule `p` to return at time `T + S` by pushing `(T+S, p)` onto `returning`. If `available` is empty, nobody gets the noodles; skip.

After all events, print each `total[i]`.

## Edge cases
- Empty row at an event: just skip (sample 1, time 100).
- Single person repeatedly going out and returning before the next event (sample 3): the return step at the top of each event reinserts them in time.
- Large values (up to 1e9, sums up to ~2e14): fits in 64-bit, and Python ints are unbounded.
- Times can tie between events and returns; `<=` handles the "present at X" rule.

## Complexity
O((N + M) log(N+M)) time, O(N+M) space. Use fast input via `sys.stdin`.

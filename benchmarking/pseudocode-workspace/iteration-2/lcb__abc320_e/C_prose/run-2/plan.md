# Plan: Flowing Noodles

## Input/output contract
Read `N M` then `M` lines of `T_i W_i S_i`, with events given in strictly
increasing time order. Output `N` lines, line `i` being the total noodles
person `i` received.

## Data structures
We need two priority queues (min-heaps):
- `available`: a heap of person indices that are currently in the row,
  ordered by index (front of row = smallest index). Initially all of
  `1..N` are available.
- `returning`: a heap of `(return_time, person_index)` for people who have
  stepped out and will rejoin the row at `return_time`.

An array `total[1..N]` accumulates noodles, initialised to 0.

## Algorithm
Process events in the given time order. For each event `(T, W, S)`:
1. Pop every entry from `returning` whose `return_time <= T` (they are back
   in the row at time T, since returning at X counts as present at X) and
   push their indices back into `available`.
2. If `available` is non-empty, pop the smallest index `p` (frontmost
   person). Add `W` to `total[p]`. Push `(T + S, p)` into `returning`.
   If `available` is empty, the noodles are lost.

After all events, print `total[i]` for `i` from 1 to N.

## Edge cases
- No one in the row at an event: noodles discarded, no state change.
- Multiple people return at the same time as / before an event: all flushed
  before serving.
- A person who returns exactly at time T is eligible at T (use `<= T`).
- Large values: amounts up to M * 1e9 = 2e14, fits in Python int easily.
- N up to 2e5 with M up to 2e5: heap operations are O((N+M) log N), fine.

## Complexity
Time O((N + M) log N), memory O(N + M).

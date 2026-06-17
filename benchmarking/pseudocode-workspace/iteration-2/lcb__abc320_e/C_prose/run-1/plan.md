# Plan: Flowing Noodles

## Input/output contract
Read `N M` then `M` lines of `T_i W_i S_i`. Output `N` lines, the i-th being the
total noodles person `i` received. Events arrive sorted by strictly increasing
`T_i`.

## Data
- `result[1..N]`: accumulated noodles per person, integers (can be large, but
  Python ints are unbounded).
- An **available** min-heap keyed by person index: holds the indices of people
  currently in the row. Smaller index = closer to front, so the front person is
  the minimum index available. Initialise with all of `1..N`.
- A **returning** min-heap keyed by return-time: entries `(return_time, person)`
  for people who have stepped out and will come back.

## Algorithm
Process events in time order. For each event at time `T` with amount `W` and
delay `S`:
1. **Process returns first**: pop every entry from the returning heap whose
   `return_time <= T` and push that person's index back onto the available heap.
   This is correct because a person returning at exactly time `X` is in the row
   at time `X`.
2. **Serve**: if the available heap is non-empty, pop the smallest index
   `p` (front of the row). Add `W` to `result[p]`. The person leaves, returning
   at `T + S`, so push `(T + S, p)` onto the returning heap.
   If the available heap is empty, the noodles are lost (no one gets them).

Because events are already sorted by `T`, no extra sorting is needed. Each
person is pushed/popped O(1) amortized per event, giving O((N+M) log N) overall.

## Edge cases
- No one in the row when noodles flow: skip (handled by emptiness check).
- Multiple people returning before/at the same event time: drain the returning
  heap fully each step.
- A person returning at exactly `T` is eligible (use `<=`).
- Large values: use Python's arbitrary-precision ints; sum can reach ~2e5 * 1e9.

## Output
Print `result[1..N]`, one per line, using a buffered join for speed.

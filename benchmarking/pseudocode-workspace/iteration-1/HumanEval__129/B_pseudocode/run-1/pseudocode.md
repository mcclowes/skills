# minPath plan

Verdict: logic-heavy with a non-obvious key insight (greedy/lexicographic path on a grid). Planning first.

## Data & invariants
- grid: N×N, contains every integer in [1, N*N] exactly once. So value 1 is always present and unique.
- k: positive integer, path length = number of cells visited (with repetition allowed).
- Output: list of k values, lexicographically minimal among all length-k walks.

## Key insight
- The lexicographically smallest first element must be the global minimum value reachable = 1 (it's always on the grid, and we may start anywhere).
- After standing on the cell holding 1, the next-smallest continuation is the minimum value among 1's orthogonal neighbors; call it `b`.
- From 1 we can step to `b`, then step back to 1, then to `b`, ... indefinitely, because 1 and b are adjacent. No other walk can beat this: position 1 = 1 (minimal), position 2 = b (smallest neighbor of 1, and any path with value 1 at pos1 must move to a neighbor of 1), and the alternation keeps repeating the two smallest reachable so the whole sequence is minimal.
- Therefore answer alternates: index even (0-based) -> 1, index odd -> b.
- Special case k == 1 -> just [1].

## Control flow
1. N = len(grid).
2. Find cell (r,c) where grid[r][c] == 1.
3. b = min over orthogonal neighbors (up/down/left/right, in bounds) of grid value.
   - N >= 2 guarantees at least one in-bounds neighbor.
4. Build result of length k: for i in 0..k-1: append 1 if i even else b.

## Edge cases & failure modes
- k == 1 -> [1] (loop with only even index, b never used; safe even if b computed).
- N == 2 -> cell with 1 has 2 neighbors; min still well-defined.
- 1 located at a corner/edge -> still has >=1 neighbor; neighbor loop only considers in-bounds.

## Interface contract
- Pure function; does not mutate grid. Returns a new list of ints of length k.

# minPath plan

Verdict: logic-heavy — lexicographic minimization with a key insight about value 1. Planning first.

## Key insight
Every value in [1, N*N] appears exactly once. So value `1` exists at a unique cell.
The lexicographically smallest path starts with the smallest possible first value, then
smallest second value, etc. Since we may start anywhere and move freely, the optimal path:
- step 1: must be the smallest reachable starting value overall → `1` (it exists somewhere).
- step 2 onward: from the cell holding `1`, the smallest neighbor value, call it `m`.
  Then we just oscillate between `1` and `m` (1, m, 1, m, ...) because after reaching `1`
  we want the smallest next value = m, then back to 1 (which is < m), then m again, etc.
  `1`'s smallest neighbor `m` is the smallest value adjacent to 1; alternating 1,m is optimal.

Why oscillation is optimal: lexicographic order is greedy position by position.
- Position 1: smallest achievable = 1 (always reachable since we choose start).
- Position 2: given we're at 1, smallest neighbor = m. Can't do better.
- Position 3: from m, we want smallest = go back to 1 (1 is a neighbor of m, and 1 is the
  global min so nothing beats it). 
- Position 4: from 1 again, smallest neighbor = m again.
So sequence is [1, m, 1, m, ...] of length k.

## Data & invariants
- grid: N x N, values a permutation of [1, N*N], N >= 2.
- k: positive integer (length of path = number of cells visited).
- Invariant: value 1 has at least one neighbor (N>=2 guarantees grid has >=2 cells, and any
  cell in an N>=2 grid has at least one edge-neighbor). So m is well-defined.

## Control flow
1. Locate cell (r,c) where grid[r][c] == 1.
2. m ← min over neighbors (up/down/left/right, in-bounds) of grid value.
3. Build result list of length k by alternating: index even → 1, index odd → m.
   (0-based: position 0 = 1, position 1 = m, position 2 = 1, ...)
4. Return result.

## Edge cases
- k == 1 → return [1] (only the start cell; loop produces just [1]).
- k == 2 → [1, m].
- N == 2 → still has neighbors; fine.
- Multiple neighbors → take min.

## Interface contract
- Input: grid (list of lists of ints), k (positive int).
- Output: list of ints length k, alternating 1 and m starting with 1.
- Pure; does not mutate grid.

# minPath plan

Verdict: logic-heavy (lexicographic minimization over paths). Planning first.

## Key observation
Values 1..N*N are a permutation, all distinct. The lexicographically smallest
length-k value sequence must START with the globally smallest value reachable as
a start — which is 1 (it's in the grid, can start anywhere). So lst[0] = 1.

After standing on the cell with value 1, the next value should be as small as
possible: pick the minimum value among 1's edge-neighbors, call it m. m >= 2
(since 1 is unique and is at the current cell). Then from that neighbor, the
smallest next value is back to 1 (1 is its neighbor and is the global min).
So the path becomes: 1, m, 1, m, 1, ... alternating.

Therefore answer = for i in 0..k-1: 1 if i even else m.

## Data & invariants
- grid: N x N, N>=2, contains each int in [1, N*N] exactly once.
- m = min over the 4-neighbors of the cell holding value 1.
- Invariant: 1 is the global minimum, so it's the optimal value to revisit
  whenever it's adjacent (it always is, from m's cell).

## Control flow
- locate cell (r,c) where grid[r][c] == 1
- m = min(grid[nr][nc]) over in-bounds neighbors (up/down/left/right)
- build result of length k: even index -> 1, odd index -> m

## Edge cases
- k == 1 -> return [1] (loop produces just the single min, matches example 2)
- N == 2 -> 1 still has >=2 neighbors; min well-defined.
- 1 in a corner -> still has 2 neighbors; fine.

## Interface contract
- input: grid (list of lists of int), k (positive int)
- output: list of k ints, the value sequence
- pure; grid not mutated

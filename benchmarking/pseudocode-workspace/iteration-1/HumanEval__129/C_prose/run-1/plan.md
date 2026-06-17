# Plan for minPath

## Contract
- Input: `grid`, an N x N list of lists (N >= 2) where every integer in [1, N*N]
  appears exactly once; `k`, a positive integer (path length = number of cells visited).
- Output: an ordered list of `k` integers, the values along the lexicographically
  smallest path of length k. The answer is guaranteed unique.

## Key insight
Because 1 is the global minimum value and it always appears somewhere in the grid,
the lexicographically smallest path must start at the cell holding 1. Any path not
starting with 1 is immediately larger at index 0. Once standing on the cell with
value 1, the smallest possible next value is the minimum value among its edge
neighbors (up/down/left/right). Call that `m`. Since N >= 2, the cell with 1 always
has at least one neighbor, so `m` exists. From the neighbor we can always step back
to 1, and from 1 step back to the neighbor, so the optimal path oscillates: 1, m, 1,
m, ... This greedy alternation is optimal because after a 1 the best follow-up is the
minimum neighbor m, and after m the best follow-up is 1 (1 is the global minimum and
m is adjacent to it). No other arrangement can be lexicographically smaller.

## Algorithm
1. Determine N from the grid dimensions.
2. Scan all cells to locate the position (r, c) of value 1.
3. Examine the four edge neighbors of (r, c), staying within bounds; take the
   minimum neighbor value `m`.
4. Build the result of length k by alternating: even indices (0-based) -> 1,
   odd indices -> m.

## Edge cases
- k == 1: result is just `[1]` (only the starting cell).
- Boundary/corner cells: neighbor enumeration is bounds-checked, so corners with
  only two neighbors still work.
- Larger k: simple alternation handles any positive k.

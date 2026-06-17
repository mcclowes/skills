# Plan for minPath

## Input/output contract
- Input: `grid`, an N x N list of lists of integers (N >= 2), containing every integer in [1, N*N] exactly once; and `k`, a positive integer (the path length, i.e. number of cells visited).
- Output: a list of `k` integers, the values of the cells along the lexicographically smallest valid path.

## Key observation
Every integer in [1, N*N] appears exactly once, so the value 1 sits in exactly one cell, and 1 is the global minimum. A path is compared lexicographically by the sequence of values it visits. To minimize lexicographically, the first value should be as small as possible: that is 1, achieved by starting on the cell holding 1.

For the second step we must move to an edge-adjacent neighbor. To keep the sequence smallest, pick the neighbor with the smallest value; call it `m`. Since N >= 2, the 1-cell always has at least one neighbor, and every value other than 1 is >= 2, so `m >= 2`.

From the neighbor we can step back to the 1-cell (value 1), which is the smallest possible value again. So the optimal path oscillates: 1, m, 1, m, 1, ... This is provably the lexicographically minimal sequence and the problem guarantees uniqueness.

## Algorithm
1. Locate the cell with value 1.
2. Examine its up/down/left/right neighbors (bounded by the grid); take the minimum neighbor value `m`.
3. Build a list of length k alternating 1 and m, starting with 1.

## Edge cases
- k = 1: output is just [1].
- Corner/edge placement of the 1-cell: neighbor scan respects grid bounds.

# Plan for minPath

## Input/output contract
- Input: `grid`, an N x N list of lists of integers (N >= 2), where every integer
  in `[1, N*N]` appears exactly once; and `k`, a positive integer giving the path
  length (number of cells visited, repetition allowed).
- Output: a list of `k` integers — the values along the lexicographically smallest
  path of length k.

## Key insight
The value 1 is unique and is the globally smallest value. Any lexicographically
minimal path of length >= 2 must include cell containing 1 as much as possible.
The optimal strategy: stand on the cell holding 1 and step back and forth between
it and its smallest-valued orthogonal neighbor. Call that neighbor value `m`.
Then the minimal sequence is `1, m, 1, m, ...` of length k (because after a 1 we
can always return to 1 from the neighbor, and 1 is the smallest possible value at
every odd position; at every even position we want the smallest reachable value
from 1, which is `m`).

## Algorithm steps
1. Determine N from the grid.
2. Locate the cell `(r, c)` whose value is 1 by scanning the grid.
3. Examine its up/down/left/right neighbors that lie inside the grid; take the
   minimum of their values as `m`. (N >= 2 guarantees at least one neighbor.)
4. Build the result list of length k: positions alternate, starting with 1 at
   index 0, then `m`, then 1, then `m`, ...
5. Return that list.

## Edge cases
- `k == 1`: result is just `[1]`; the alternation naturally produces this.
- Cell with 1 in a corner or edge: still has at least one in-grid neighbor (N>=2).
- Large k: simple alternation, O(k) construction.

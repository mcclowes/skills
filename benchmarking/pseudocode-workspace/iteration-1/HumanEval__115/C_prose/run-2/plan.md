# Plan: max_fill

## Input/output contract
- Input: `grid`, a rectangular 2D list where each row is a well and each cell is `0` (empty) or `1` (one unit of water); `capacity`, a positive integer (1..10) giving the bucket capacity shared by all wells.
- Output: an integer — the total number of times any bucket must be lowered to empty every well.

## Data involved
Each row's water amount is the sum of its entries (count of 1s). A single bucket of size `capacity` can remove up to `capacity` units per lowering. To empty a row holding `w` units, we need `ceil(w / capacity)` lowerings. The answer is the sum of these per-row lowering counts across all rows.

## Algorithm steps
1. Initialize a running total to 0.
2. For each row in the grid:
   a. Compute `w = sum(row)`, the number of water units in that well.
   b. Compute the lowerings for this well as `ceil(w / capacity)`, using `math.ceil`. This naturally yields 0 when `w` is 0, since `ceil(0 / capacity) == 0`.
   c. Add that to the running total.
3. Return the total.

## Edge cases
- All-zero grid (Example 3): each row contributes 0, so total is 0.
- A well with fewer units than capacity: still needs exactly 1 lowering (the partial bucket counts).
- A well exactly divisible by capacity: needs `w / capacity` lowerings, no extra.
- Capacity larger than any row sum: every non-empty row needs exactly 1 lowering.
- Single row or single column grids are handled the same way.

## Notes
Use `math.ceil` for clarity; division by `capacity` is always safe since `capacity >= 1`.

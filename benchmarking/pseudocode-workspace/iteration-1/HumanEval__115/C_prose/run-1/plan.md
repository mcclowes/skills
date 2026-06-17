# Plan for max_fill

## Input/output contract

The function `max_fill(grid, capacity)` takes a rectangular 2D list `grid` where each
inner list (row) represents one well, and each `1` is a unit of water (a `0` is empty
space). The integer `capacity` is the shared bucket capacity for every well. The
function returns a single integer: the total number of times a bucket must be lowered
to empty all wells.

## Algorithm

Each well is independent. For a given well, the amount of water it holds is the count of
`1`s in that row. A bucket of size `capacity` can remove up to `capacity` units per
lowering, so the number of lowerings needed for that well is the water divided by
capacity, rounded up: `ceil(water / capacity)`. The total answer is the sum of these
per-well lowering counts across all rows.

Steps:
1. Initialise a running total of `0`.
2. For each row in the grid, compute `water = sum(row)` (counts the `1`s since values
   are only `0` or `1`).
3. Add `ceil(water / capacity)` to the total. I'll use `math.ceil`.
4. Return the total.

## Edge cases

- An empty/dry well (all `0`s) contributes `0` lowerings since `ceil(0 / capacity) == 0`.
  Example 3 confirms this: every row sums to `0`, so the result is `0`.
- Capacity larger than the water in a well still requires one lowering if any water is
  present, which `ceil` handles correctly.
- Capacity is guaranteed `>= 1`, so no division-by-zero concern.
- Grid dimensions are bounded (up to 100x100) and values are strictly `0` or `1`, so
  `sum(row)` is a safe way to count water.

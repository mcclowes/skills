# Plan for max_fill

## Problem

We are given a rectangular grid where each row represents a well and each `1` is
one unit of water. Every well has a bucket with the same fixed `capacity`. Each
time we lower a bucket into a well we can remove up to `capacity` units of water
from that well in a single dip. We must report the total number of bucket
lowerings needed to empty every well.

## Input / output contract

- Input: `grid`, a list of lists of integers (each entry `0` or `1`); and
  `capacity`, a positive integer (`1 <= capacity <= 10`).
- Output: a single integer — the total number of bucket dips across all wells.

## Algorithm

For each row (well), count the units of water by summing the row (since entries
are `0`/`1`, the sum is the count of ones). A bucket holds `capacity` units, so
the number of dips needed to empty that single well is the count divided by
capacity, rounded up: `ceil(units / capacity)`. Summing these per-well dip counts
gives the answer. I'll implement `ceil` via `math.ceil` for clarity. The buckets
are per-well, so wells are handled independently and never combined.

## Edge cases

- A well that is already empty (all zeros) contributes `0` dips because
  `ceil(0 / capacity) == 0`; no special-casing needed.
- A fully empty grid returns `0` (Example 3).
- Capacity larger than any well's water count means each non-empty well needs
  exactly one dip.
- Constraints guarantee grid is non-empty and rectangular, so no empty-grid or
  ragged-row handling is required.

## Verification against examples

- Example 1: rows sum to 1, 1, 4 with capacity 1 -> 1+1+4 = 6. Correct.
- Example 2: rows sum to 2, 0, 4, 3 with capacity 2 -> 1+0+2+2 = 5. Correct.
- Example 3: all zeros -> 0. Correct.

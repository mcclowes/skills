# Plan: merge_weighted_intervals

## Input / output contract
- Input: a list of tuples `(start, end, weight)`. Each tuple has `start < end`
  and `weight` is a number (int or float). The list is unordered and may be
  empty.
- Output: a list of `(start, end, weight)` tuples representing merged groups,
  sorted by `start` ascending. Each output interval spans `[min start, max end)`
  of its group and carries the sum of all member weights.

## Semantics
Intervals are half-open `[start, end)`. Two intervals overlap only if they share
more than a single point, i.e. they have positive-length intersection. Touching
intervals (one ends exactly where the next begins, `prev_end == next_start`) do
NOT overlap and must stay separate. Overlap is transitive, so a chain A-B-C all
merges into one even if A and C are disjoint.

## Algorithm (sweep after sort)
1. Handle the empty input: return `[]`.
2. Sort intervals by `start` ascending (ties don't matter for correctness).
3. Initialise the first group from the first interval: track `cur_start`,
   `cur_end`, `cur_weight`.
4. Iterate over the remaining intervals. For each `(s, e, w)`:
   - It overlaps the current group iff `s < cur_end` (strict; equality means a
     touch, which does not merge). Because we sorted by start, `s >= cur_start`,
     so this single comparison suffices and overlap is naturally transitive
     through `cur_end` extension.
   - If overlapping: extend `cur_end = max(cur_end, e)` and add `w` to weight.
   - Otherwise: emit the current group, then start a new group from `(s, e, w)`.
5. Emit the final group.

## Edge cases
- Empty list -> `[]`.
- Single interval -> returned unchanged.
- Exactly touching intervals -> kept separate (`s < cur_end` is false).
- Fully nested interval (e overlaps but ends earlier) -> `max` keeps the wider
  end; weight still summed.
- Negative or float weights -> summed normally.
- Duplicate intervals -> overlap, weights add.
- The output tuples preserve original numeric types via `+` and `max`.

Sorting is O(n log n); the sweep is O(n). This is correct and efficient.

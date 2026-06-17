# Plan: merge_weighted_intervals

## Input/output contract
- Input: `intervals`, a list of tuples `(start, end, weight)`. Each has `start < end`; `weight` is any number (int/float, possibly negative). The list is not sorted and may be empty.
- Output: a list of `(start, end, weight)` tuples sorted by `start` ascending. Each output interval is the union span of a maximal cluster of transitively-overlapping inputs, with `weight` equal to the sum of the merged inputs' weights. Touching intervals (one's `end` equals the next's `start`) do NOT merge because intervals are half-open `[start, end)`.

## Algorithm
1. Handle the empty input: return `[]` immediately.
2. Sort the intervals by `start` ascending (ties broken by `end`, harmless). Sorting guarantees that any interval overlapping the current open cluster must overlap the cluster's running maximum `end`, which lets us do a single linear sweep.
3. Initialize the first cluster from the first sorted interval: track `cur_start`, `cur_end`, `cur_weight`.
4. For each subsequent interval `(s, e, w)`:
   - Overlap test: two half-open intervals `[a,b)` and `[s,e)` overlap (share more than a point) iff `s < cur_end`. Equality (`s == cur_end`) is mere touching and does NOT count as overlap.
   - If `s < cur_end`: merge — keep `cur_start`, extend `cur_end = max(cur_end, e)`, add `cur_weight += w`.
   - Else: close out the current cluster (append it), then start a new cluster from `(s, e, w)`.
5. After the loop, append the final open cluster.
6. Result is already sorted by start because we processed in sorted order.

## Edge cases
- Empty list -> `[]`.
- Single interval -> returned unchanged.
- Fully nested intervals (`[1,10)` containing `[2,3)`): `max` on end keeps the wider span; weights still sum.
- Transitive chains: the running `cur_end` grows as we merge, so a later interval overlapping the extended span merges even if disjoint from the first.
- Touching boundaries kept separate (`s == cur_end`).
- Negative weights summed normally.
- Equal starts merge (overlap since both start before either ends).

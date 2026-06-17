# Plan: merge_weighted_intervals

## Input / output contract
The function takes `intervals`, a list of `(start, end, weight)` tuples where
`start < end` and `weight` is a number (int or float). It returns a list of
merged `(start, end, weight)` tuples sorted by `start` ascending. The input is
not assumed to be sorted, and the original list should not be mutated.

## Data and semantics
Intervals are half-open `[start, end)`. Two intervals overlap only if they
share more than a single point, i.e. they have a positive-length intersection.
For sorted intervals where `prev` precedes `cur`, they overlap when
`cur.start < prev.end`. Crucially, mere touching (`cur.start == prev.end`) is
NOT an overlap, so the comparison is strict `<`, not `<=`. Overlap is
transitive, so a running sweep that tracks the current cluster's maximum end
naturally chains A-B-C even when A and C are themselves disjoint.

## Algorithm
1. If the input is empty, return an empty list.
2. Sort a copy of the intervals by `start` (ties broken by `end`).
3. Initialize the result with the first interval's values, tracking the
   current cluster's `cur_start`, `cur_end`, and accumulated `cur_weight`.
4. For each subsequent interval `(s, e, w)`:
   - If `s < cur_end` (strict — touching does not merge), it overlaps the
     current cluster: extend `cur_end = max(cur_end, e)` and add `w` to
     `cur_weight`.
   - Otherwise, close out the current cluster by appending it, then start a new
     cluster from this interval.
5. Append the final open cluster.

## Edge cases
- Empty input -> empty list.
- Single interval -> returned unchanged (as a tuple).
- Touching intervals (`end == next start`) stay separate.
- Fully nested intervals: `max` on `end` keeps the outer span; weights still sum.
- Duplicate/identical intervals merge and sum.
- Negative or float weights sum correctly.
- Unsorted input handled by the initial sort.

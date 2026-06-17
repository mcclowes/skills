# Plan: merge_weighted_intervals

## Input/output contract
- Input: `intervals`, a list of tuples `(start, end, weight)` where `start < end`
  and `weight` is numeric. The list is not sorted and may be empty.
- Output: a list of `(start, end, weight)` tuples sorted by `start` ascending.
  Each output interval spans `[min start, max end)` of a maximal group of
  transitively-overlapping inputs, and its weight is the sum of the group's
  weights.

## Key semantics
- Intervals are half-open `[start, end)`. Two intervals overlap only if they
  share more than a single point. Concretely, intervals `A` and `B` overlap iff
  `A.start < B.end and B.start < A.end`. Mere touching (`A.end == B.start`)
  does NOT count as overlap, because the shared boundary is a single point.
- Overlap is transitive: a chain A–B–C all merges into one even if A and C are
  disjoint. The standard sweep handles this naturally.

## Algorithm
1. Handle the empty input: return `[]`.
2. Sort the intervals by `start` ascending (ties don't matter for correctness).
3. Initialize the result with the first interval as the current open group:
   track `cur_start`, `cur_end`, `cur_weight`.
4. Iterate over the remaining intervals. For each `(s, e, w)`:
   - If `s < cur_end` (strict — touching means `s == cur_end`, which does not
     extend, so it starts a new group): the new interval overlaps the current
     group. Extend `cur_end = max(cur_end, e)` and add `w` to `cur_weight`.
   - Otherwise: the current group is complete. Append it, then start a fresh
     group from `(s, e, w)`.
5. After the loop, append the final pending group.

Because intervals are sorted by start, any interval that overlaps the running
group has `s < cur_end`; once `s >= cur_end` no later interval (with even larger
start) can reach back, so closing the group is safe.

## Edge cases
- Empty input -> `[]`.
- Single interval -> returned unchanged.
- Exactly touching intervals -> kept separate (the `<` comparison).
- Nested interval fully inside another -> merges, `cur_end` via `max`.
- Negative or float weights -> summed normally.
- Duplicate starts -> handled by the comparison; sort stability is irrelevant.

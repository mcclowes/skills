# Plan: merge_weighted_intervals

## Input/output contract
- Input: a list of tuples `(start, end, weight)`, each with `start < end` and `weight` a number. The list may be empty and is not necessarily sorted.
- Output: a list of `(start, end, weight)` tuples, sorted by `start` ascending, where overlapping intervals have been merged. A merged interval spans `[min start, max end)` of its members and carries the SUM of their weights.

## Key semantics
Intervals are half-open `[start, end)`. Two intervals *overlap* only if they share more than a single point — i.e. they have a positive-length intersection. For sorted intervals `prev` and `cur`, they overlap iff `cur.start < prev.end` (strict). If `cur.start == prev.end` they merely touch and must NOT merge. Overlap is transitive, so chains of overlapping intervals collapse into one.

## Algorithm steps
1. Handle the empty input: return `[]`.
2. Sort the intervals by `start` ascending (a stable sort on the first element suffices; ties don't affect correctness).
3. Sweep left to right, maintaining a current accumulator `(cur_start, cur_end, cur_weight)` seeded from the first interval.
4. For each subsequent interval `(s, e, w)`:
   - If `s < cur_end` (strict overlap): extend the accumulator — `cur_end = max(cur_end, e)`, `cur_weight += w`. We keep `cur_start` (already the min because sorted). Using `cur_end` (the running max end of the whole chain) is what makes overlap transitive: a later interval overlapping any earlier member of the chain is captured.
   - Else (touching or disjoint): emit the accumulator and reset it to `(s, e, w)`.
5. After the loop, emit the final accumulator.

## Edge cases
- Empty list -> `[]`.
- Single interval -> returned unchanged.
- Touching intervals (`s == cur_end`) -> not merged.
- Fully nested intervals (`e < cur_end`) -> merged; `max` preserves the outer end.
- Negative or zero weights -> just summed normally.
- Duplicate intervals -> merged, weights summed.
- Unsorted input -> handled by the initial sort.

# Plan: merge_weighted_intervals

## Contract
Input: `intervals`, an iterable of `(start, end, weight)` tuples where
`start < end` and `weight` is a number (int or float). The input is not
necessarily sorted and may be empty. Output: a list of `(start, end, weight)`
tuples sorted by `start` ascending, where every group of transitively
overlapping intervals has been merged into a single interval spanning
`[min start, max end)` with weight equal to the sum of all member weights.

## Key semantics
Intervals are half-open `[start, end)`. Two intervals overlap only if they
share more than a single point — i.e. they overlap iff `a.start < b.end` and
`b.start < a.end` using strict inequality. Mere touching (`a.end == b.start`)
does NOT count as overlap, so `[1,2)` and `[2,3)` stay separate. Overlap is
transitive: a chain A–B–C all merges even when A and C are disjoint.

## Algorithm
1. Sort the intervals by `start` ascending (then `end`).
2. Sweep left to right, maintaining the current open cluster's
   `cur_start`, `cur_end`, `cur_weight`.
3. For each next interval, it joins the current cluster iff
   `next_start < cur_end` (strict — touching does not merge). When it joins,
   extend `cur_end = max(cur_end, next_end)` and add its weight.
4. Otherwise, emit the current cluster and start a new one.
5. Emit the final cluster.

Using `cur_end` (the running max end) for the overlap test correctly captures
transitivity, since the cluster's reach only ever grows.

## Edge cases
- Empty input -> `[]`.
- Single interval -> returned unchanged (as a tuple).
- Nested intervals (one fully inside another) -> merge; max end preserved.
- Touching boundaries -> not merged.
- Negative or float weights and coordinates -> handled (only comparison and
  addition used).
- Preserve original tuple weight type by summing without coercion.

# merge_weighted_intervals — plan

Verdict: invariant-heavy (half-open overlap, transitive grouping, weight sums) — planning first.

## Data & invariants
- Input: list of (start, end, weight), start < end, weight numeric. Unsorted.
- Half-open [start, end): overlap means they share MORE than a point, i.e. cur.start < group.end (strict). Touching (cur.start == group.end) does NOT overlap.
- Output: list of (start, end, weight), sorted by start ascending, pairwise non-overlapping under the half-open rule.
- Invariant while building a group: group.end is the running max end; group.weight is the running sum of all members' weights; group.start stays the first (min) start since input is start-sorted.

## Control flow
```
if intervals empty → return []
sort intervals by start ascending   # ties on start don't matter for correctness
result ← empty list
cur_start, cur_end, cur_w ← first interval
for each (s, e, w) in sorted[1:]:
    if s < cur_end:                  # STRICT: overlap (share > point)
        cur_end ← max(cur_end, e)    # extend, never shrink (handles nesting)
        cur_w   ← cur_w + w          # accumulate weight
    else:                            # s >= cur_end: disjoint OR merely touching
        append (cur_start, cur_end, cur_w)
        cur_start, cur_end, cur_w ← s, e, w
append (cur_start, cur_end, cur_w)   # flush last group
return result
```

## Edge cases & failure modes
- empty input → []
- single interval → [itself], weight unchanged.
- touching [1,2),[2,3): s(2) < cur_end(2) is false → kept separate. Correct.
- transitive A[1,3] B[2,4] C[3.5,6]: B extends end to 4, C.start 3.5 < 4 merges, even though A and C disjoint. Running cur_end carries transitivity.
- fully nested [1,9] then [2,3]: 2 < 9 merge, max(9,3)=9 keeps outer end.
- unsorted input handled by sort step.
- weights can be negative/float — plain sum, no assumptions.

## Interface contract
- Pure: does not mutate input (sort a copy). Returns new list of tuples.
- No validation of start<end assumed beyond contract.

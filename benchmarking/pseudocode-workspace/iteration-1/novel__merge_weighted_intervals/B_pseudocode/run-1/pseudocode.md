# merge_weighted_intervals

Verdict: logic-heavy — half-open overlap (touching ≠ overlap), transitive merging, weight summation. Plan first.

## Data & invariants
- Input: list of (start, end, weight), start < end, weight numeric. Not sorted.
- Output: list of (start, end, weight) sorted by start ascending; runs are pairwise non-overlapping.
- Overlap (half-open): A=[s1,e1), B=[s2,e2) overlap iff s1 < e2 AND s2 < e1.
  After sorting by start (s2 ≥ s1), this reduces to: s2 < e1 (strict). Touching s2 == e1 → NOT overlap.
- Invariant during scan: `cur_end` = max end seen in current run; a new interval joins the run iff its start < cur_end (strict).

## Control flow
```
if input empty → return []
sort intervals by start ascending
result ← empty list
cur_start, cur_end, cur_weight ← first interval's (s, e, w)
for each (s, e, w) in sorted order[1:]:
    if s < cur_end:                       # strict: overlap, merge
        cur_end ← max(cur_end, e)         # extend, don't shrink (nested case)
        cur_weight ← cur_weight + w
    else:                                  # s >= cur_end: disjoint or touching
        append (cur_start, cur_end, cur_weight)
        cur_start, cur_end, cur_weight ← s, e, w
append (cur_start, cur_end, cur_weight)    # flush final run
return result
```
Transitivity handled naturally: cur_end grows as run extends, so chained overlaps fold into one run.

## Edge cases & failure modes
- empty input            → return []
- single interval        → return [that interval] unchanged
- touching [1,2),[2,3)   → s=2, cur_end=2, 2 < 2 false → separate. Correct (uses <, not ≤).
- nested [1,9,a],[2,3,b]  → 2<9 merge, max(9,3)=9 keeps outer end, weight a+b.
- transitive [1,3],[2,5],[4,6] → run extends 3→5→6, all merged.
- equal starts [1,4],[1,2] → after sort either order; second start < cur_end → merge (overlap, share interior).
- negative/float weights → just summed, no special handling.

## Interface contract
- Pure; does not mutate input. Returns new list of tuples.
- No validation of start<end assumed (trusted per docstring).

# merge_weighted_intervals — plan

Verdict: logic-heavy. Half-open overlap rule (touching ≠ overlap), transitive
merging, and weight accumulation across a run. Off-by-one on `>` vs `≥` is the
whole game. Planning first.

## Data & invariants
- Input: list of (start, end, weight); start < end; weight numeric. Unsorted.
- Output: list of (start, end, weight), sorted by start ascending, pairwise
  non-overlapping (may touch).
- Invariant: while building a run, `cur_end` = max end of all intervals folded
  in so far; `cur_weight` = sum of their weights; `cur_start` = the start of the
  first (earliest-start) interval in the run.
- Half-open [start, end): two intervals overlap iff they share more than a point,
  i.e. next.start < cur_end (strict). next.start == cur_end → touching → NOT
  overlapping.

## Control flow
```
if input empty → return []
sorted ← input sorted by start ascending
result ← empty list
cur_start, cur_end, cur_weight ← first interval's (s, e, w)
for each (s, e, w) in sorted[1:]:
    if s < cur_end:                 # strict: overlap, not mere touch
        cur_end ← max(cur_end, e)   # extend, never shrink (handles nesting)
        cur_weight ← cur_weight + w # accumulate
        # cur_start unchanged (sorted ⇒ already the min start)
    else:                           # s >= cur_end: disjoint or touching
        append (cur_start, cur_end, cur_weight)
        cur_start, cur_end, cur_weight ← s, e, w
append (cur_start, cur_end, cur_weight)   # flush final run
return result
```

## Edge cases & failure modes
- empty input → [] (handled by early return).
- single interval → returned unchanged as one tuple.
- touching [1,2),[2,3): s==cur_end → `s < cur_end` false → kept separate. Correct.
- transitive A=[1,3] B=[2,4] C=[3,5]: sorted; B overlaps A (2<3) → cur_end 4;
  C: 3<4 → cur_end 5. All merged even though A and C disjoint. Handled by
  comparing against running cur_end, not the first interval's end.
- fully nested [1,9] containing [2,3]: 2<9 merge, max keeps end 9. Handled.
- duplicate starts: stable; both fold into same run since second start < cur_end
  (start<end guarantees cur_end>first start). Weights sum.
- equal start same as cur_start: still < cur_end, merges.

## Interface contract
- Pure; does not mutate input. Returns a new list of tuples.
- No validation of start<end assumed-good per spec; numeric weights summed as-is
  (int+int→int, float preserved).

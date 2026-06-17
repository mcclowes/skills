# merge_weighted_intervals — plan

Verdict: logic-heavy. Subtle invariant = half-open overlap (touching ≠ overlap),
transitive merging, weight summation. Plan first.

## Data & invariants
- Input: list of tuples (start, end, weight), start < end, weight numeric.
- Output: list of (start, end, weight) sorted by start ascending, runs disjoint
  (in the "share more than a point" sense: each output run's end < next run's start
  OR they only touch — i.e. no two output runs overlap).
- Overlap definition for [s1,e1) and [s2,e2) where s1 ≤ s2 (after sort):
    they overlap iff s2 < e1   (strict: equal endpoints = touching = NOT overlap).
- Invariant during sweep: `cur_end` = max end seen so far in the current run;
  `cur_weight` = sum of weights of all intervals folded into current run;
  `cur_start` = start of the run's first (leftmost) interval (= min start, since sorted).

## Control flow
sort intervals by start ascending (ties: order irrelevant for correctness)
result ← empty
for each iv (s, e, w) in sorted order:
  if result empty:
    start new run (cur_start=s, cur_end=e, cur_weight=w)
  else if s < cur_end:                 # STRICT < : touching does not merge
    extend run: cur_end ← max(cur_end, e); cur_weight ← cur_weight + w
  else:                                # s >= cur_end : gap or touch → new run
    flush (cur_start, cur_end, cur_weight) to result
    start new run with iv
after loop: flush final run if one is open

## Edge cases
- empty input            → return []
- single interval        → return [that interval]
- touching [1,2),[2,3)   → s=2 NOT < cur_end=2 → separate (uses strict <). Correct.
- overlap [1,3),[2,4)     → 2 < 3 → merge to [1,4), weight 5+1=6. Correct.
- transitive A,B,C where A∩C empty: B keeps run open via cur_end, so C still merges.
  e.g. [1,3),[2,6),[5,7): after A,B cur_end=6; C.start=5<6 → merges. Correct.
- fully nested [1,9),[2,3): 2<9 merge, cur_end=max(9,3)=9 (don't shrink). Correct.
- duplicate intervals    → overlap, weights summed. Correct.
- negative / float weights → just summed, no special handling.

## Interface contract
- Pure; does not mutate input.
- Returns new list of tuples. Bad-input assumptions (start<end) trusted, not validated.

# merge_weighted_intervals — plan

Verdict: logic-heavy. Subtle boundary (half-open: touching ≠ overlap), transitive
merge, weight summation. Planning first.

## Data & invariants
- Input: list of (start, end, weight), start < end, weight numeric. Not sorted.
- Output: list of (start, end, weight) sorted by start ascending.
- Invariant: output intervals are pairwise non-overlapping (may touch).
- Invariant: each output weight = sum of weights of all inputs that merged into it.
- Invariant: every input interval is accounted for in exactly one output interval.
- Half-open [start, end): overlap means they share more than a single point.
  Two intervals A, B (A sorted first) overlap iff B.start < A.end (strict).
  If B.start == A.end they merely touch → do NOT merge.

## Control flow
  if input empty → return []
  sort intervals by start ascending (ties: order irrelevant for correctness)
  result ← empty list
  for each iv (s, e, w) in sorted order:
    if result empty OR s >= last.end:        # strict: touching (s == last.end) does NOT merge
      append (s, e, w) as new run
    else:                                    # s < last.end → genuine overlap
      last.end    ← max(last.end, e)         # extend, never shrink (handles nesting)
      last.weight ← last.weight + w          # sum weights
  return result

Note on transitivity: sorting by start makes overlap detection against the running
merged interval's current end sufficient. Because we extend last.end to the max,
a later interval C that overlaps the *extended* run merges in even if it was
disjoint from the original first interval A. Comparing against last.end (the
running max end), not the last raw interval's end, is what makes this transitive.

## Edge cases & failure modes
- empty input → []
- single interval → [that interval] unchanged
- touching [1,2,_],[2,3,_] → s(=2) >= last.end(=2) → separate, NOT merged
- overlap [1,3],[2,4] → 2 < 3 → merge to [1,4], weights summed
- fully nested [1,9,a],[2,3,b] → 2 < 9, max keeps end 9 → [1,9,a+b]
- transitive [1,3],[2,5],[4,6]: 1-3 +2<3→[1,5]; 4<5→[1,6], all three summed
- duplicate identical intervals → overlap (s < end) → merged, weights summed
- negative / float weights → just summed, no special handling
- equal starts [1,5,a],[1,3,b] → second s(1) < last.end(5) → merge [1,5,a+b]

## Interface contract
- Pure function; input list not mutated (build new tuples).
- Returns new list of tuples sorted by start.
- No validation of start<end assumed-on-input; no error path specified.

# merge_weighted_intervals — plan

Verdict: logic-heavy. Half-open overlap (touching ≠ overlap), transitive merging,
weight summing. The `>=` vs `>` boundary is the bug magnet. Planning first.

## Data & invariants
- Input: list of (start, end, weight); start < end; weight numeric. Not sorted.
- Output: list of (start, end, weight), sorted by start ascending.
  - Invariant: output intervals are pairwise non-overlapping (may touch).
  - Invariant: each output weight = sum of weights of all inputs merged into it.
  - Invariant: every input belongs to exactly one output group (partition).
- Overlap def (half-open [s,e)): A and B overlap iff they share more than a point,
  i.e. A.start < B.end AND B.start < A.end. Touching (A.end == B.start) → NOT overlap.

## Control flow
- if input empty → return []
- sort intervals by start ascending (ties: any stable order is fine)
- result ← empty list of [start, end, weight]   # mutable accumulators
- for each iv (s, e, w) in sorted order:
    - if result empty OR s >= result.last.end:   # >= : touching starts new run
        append [s, e, w]                          # no overlap with current run
      else:                                       # s < last.end → overlaps run
        result.last.end ← max(result.last.end, e)  # extend, never shrink
        result.last.weight ← result.last.weight + w
- convert each [start,end,weight] to tuple, return

## Why sort-then-sweep handles transitivity
- After sorting by start, any interval overlapping the running merged interval has
  s < running.end. Extending running.end via max() carries forward the union's reach,
  so A–B–C chains absorb correctly even if A and C are disjoint (C still has
  s < running.end because B pushed running.end past C.start).
- The merged run's start is the first interval's start (smallest, since sorted) =
  min start. end is max end via max(). weight is running sum. Invariants hold.

## Edge cases
- empty input            → return []
- single interval        → return [that interval] unchanged
- touching [1,2),[2,3)   → s(=2) >= last.end(=2) → NOT merged (two outputs). Uses >=.
- nested [1,9),[2,3)     → s(2) < 9 → merge; max(9,3)=9 keeps outer end. weight summed.
- identical intervals    → overlap (s < e since width>0) → merged, weights summed.
- shared single point only is the touching case → not merged.
- negative / zero / float weights → just summed; no special handling.
- many chained overlaps  → all collapse into one via running.end extension.

## Interface contract
- Pure: does not mutate input tuples or list.
- Returns a new list of tuples sorted by start ascending.
- No error raising assumed (precondition start < end trusted).

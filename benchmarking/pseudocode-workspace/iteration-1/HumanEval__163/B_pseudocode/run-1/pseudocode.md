# generate_integers(a, b)

Verdict: borderline-trivial filter, but one subtle point: "even digits" means single-digit
even numbers (2,4,6,8) — anything ≥ 10 has no single even-digit representation, so the
effective universe is just {2,4,6,8} intersected with the range. Brief plan to pin that down.

## Data & invariants
- Inputs: a, b positive integers.
- Output: ascending list of single-digit even numbers (2,4,6,8) that lie within [min,max].
- Invariant: result is sorted ascending, contains only values from {2,4,6,8}.

## Control flow
- lo ← min(a, b); hi ← max(a, b)   # range is unordered per spec (8,2 same as 2,8)
- candidates ← [2, 4, 6, 8]        # the only even single digits
- result ← [c for c in candidates if lo ≤ c ≤ hi]
- return result (candidates already ascending → result ascending)

## Edge cases
- a > b: normalised by min/max.
- range entirely ≥ 10, e.g. (10,14): no candidate in range → [].
- range below 2, e.g. (1,1): → [].
- a == b on an even digit, e.g. (4,4): → [4].

## Interface contract
- Pure; returns new list; no mutation of inputs.

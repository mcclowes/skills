# generate_integers(a, b)

Verdict: borderline-trivial filter, but one subtle point worth naming — "even digits" means single-digit even numbers (2,4,6,8), bounded by the range, regardless of arg order. Quick plan.

## Data & invariants
- Inputs a, b: positive integers, order unspecified.
- Output: ascending list of single-digit even values (subset of {2,4,6,8}) lying within the inclusive range [min(a,b), max(a,b)].
- Invariant: result is sorted ascending and contains no duplicates (guaranteed by iterating fixed source ascending).

## Control flow
```
lo ← min(a, b)
hi ← max(a, b)
result ← []
for d in [2, 4, 6, 8]:        # candidate single-digit evens, already ascending
    if lo ≤ d ≤ hi:
        append d
return result
```

## Edge cases
- a > b (e.g. 8,2)          → normalized via min/max → [2,4,6,8]
- range above 8 (10,14)     → no candidate fits → []
- range below 2 (e.g. 0,1)  → []
- a == b on an even digit   → [that digit]; on odd/large → []

## Contract
- Pure; inputs not mutated; returns new list. No error handling needed (assumes positive ints per spec).

# generate_integers(a, b)

Borderline-trivial, but the spec wording is misleading: examples show it returns
even single-digit numbers in [2,8] that fall within the range — i.e. the even
digits 2,4,6,8 that lie between min and max. Plan to pin down the actual rule.

## Data & invariants
- Inputs: positive ints a, b (order arbitrary).
- The "even digits" are the fixed set {2, 4, 6, 8}.
- Output: ascending list of those even digits d with lo <= d <= hi.
- Invariant: output is a subset of {2,4,6,8}, sorted ascending, no dups.

## Control flow
- lo <- min(a, b); hi <- max(a, b)
- result <- [d for d in (2,4,6,8) if lo <= d <= hi]   (iterate in ascending order)
- return result

## Edge cases
- a > b (e.g. 8,2)       -> normalize with min/max -> [2,4,6,8]
- range above 8 (10,14)  -> no even digit in [10,14] -> []
- range below 2 (1,1)    -> [] 
- single point exactly on an even digit (4,4) -> [4]
- includes 0? 0 is even but not in {2,4,6,8} and examples never show it -> excluded (matches "even digits between a and b" with a,b positive; lowest shown is 2)

## Contract
- Pure. Returns new list. No mutation of inputs.

# move_one_ball

Verdict: logic-heavy (cyclic-rotation invariant, off-by-one risk on wrap-around). Plan first.

## Data & invariants
- Input: list of N unique integers, arbitrary order.
- Key fact: right shifts produce exactly the N cyclic rotations of arr.
- A cyclic rotation can be sorted iff arr has at most ONE adjacent pair (in circular order) where prev > next.
  - 0 descents → already sorted.
  - exactly 1 circular descent → the break point is the rotation seam; some rotation is sorted.
  - ≥ 2 descents → no rotation is non-decreasing.

## Control flow
```
if arr empty → return True
count ← 0
for i from 0 to N-1:                  # circular comparison
    if arr[i] > arr[(i+1) mod N]:
        count ← count + 1
return count ≤ 1
```

## Edge cases
- empty array        → True
- single element     → 0 descents → True
- already sorted     → 0 circular descents (last>first counts as 1 only if last>first; for sorted distinct, last>first so count=1) → True
  Note: for a fully sorted array, last>first gives count=1, still ≤1 → True. Correct.
- reverse sorted     → many descents → False (for N≥3)
- two elements       → at most 1 descent → always True (matches: any 2-element array is rotatable to sorted)

## Contract
- Pure; does not mutate input. Returns bool.

# move_one_ball

Verdict: small but has a subtle invariant (a rotation of a sorted array has at most one "drop"). Plan first.

## Data & invariants
- Input: list of N distinct ints, any order.
- Key fact: right shifts produce cyclic rotations. An array is some rotation of its sorted form iff, viewed cyclically, there is at most one index where arr[i] > arr[i+1].
  - 0 drops → already sorted.
  - exactly 1 drop (counting the wrap-around pair arr[N-1] vs arr[0]) → it is a rotation of sorted.
  - ≥2 drops → impossible.

## Control flow
```
if arr empty → return True
count ← number of indices i in [0, N-1] where arr[i] > arr[(i+1) mod N]
return count ≤ 1
```
The mod-N wrap pair (last vs first) must be included in the count.

## Edge cases
- empty            → True
- single element   → 0 drops → True
- already sorted   → wrap pair last>first counts as the single allowed drop → count = 1 ≤ 1 → True
- [3,4,5,1,2]      → drop at 5>1 only (2>3 wrap also? 2<3 no) → count 1 → True
- [3,5,4,1,2]      → drops 5>4 and 4>1 → count ≥2 → False

## Contract
Pure; does not mutate input; returns bool.

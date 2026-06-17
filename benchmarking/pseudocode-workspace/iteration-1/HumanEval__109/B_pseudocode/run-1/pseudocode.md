# move_one_ball

Verdict: logic with a subtle invariant (a right-rotation of a sorted array). Plan first.

## Data & invariants
- Input: array of unique integers, any order.
- Right shift = rotation: element moved from end to front. Any number of shifts = any rotation.
- Key fact: an array can be sorted by rotations iff it is a rotation of its sorted form.
- Equivalent test: the array's sorted order has at most ONE "drop" point (index where arr[i] > arr[i+1]), when viewed cyclically. A sorted array has 0 drops; a single-rotation-from-sorted array has exactly 1 drop AND the wrap-around (last element <= first element) holds.

## Control flow
```
if arr empty → return True
n ← length
count drops over i from 0 to n-1 (cyclic):
  next ← arr[(i+1) mod n]
  if arr[i] > next: drops ← drops + 1
return drops <= 1
```
Cyclic comparison automatically includes the wrap (last vs first), so a valid rotation gives exactly one internal drop at the rotation seam and zero elsewhere; fully sorted gives zero drops total.

## Edge cases
- empty → True
- single element → 0 drops → True
- already sorted → 0 drops → True
- valid rotation [3,4,5,1,2] → drop only at 5>1 → count 1 → True
- not a rotation [3,5,4,1,2] → drops at 5>4 and 4>1 → count 2 → False
- unique elements guaranteed, so no equal-adjacent ambiguity.

## Contract
- Pure; does not mutate input; returns bool.

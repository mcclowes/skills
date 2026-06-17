# max_fill

Verdict: mostly straight-line, but the per-well ceiling division has an off-by-one risk worth pinning.

## Data & invariants
- grid: list of rows, each row a list of 0/1. All rows same length.
- capacity: int >= 1.
- Output: int >= 0, total bucket lowerings.
- Invariant: a well with `w` units needs ceil(w / capacity) lowerings; an empty well needs 0 (ceil(0/c)=0, naturally handled).

## Control flow
```
total ← 0
for each row in grid:
  water ← sum of row            # count of 1s
  total ← total + ceil(water / capacity)
return total
```

## Edge cases
- empty well (all zeros)      → ceil(0/c) = 0, contributes nothing
- grid all zeros             → returns 0 (example 3)
- water exactly divisible    → ceil(c/c)=1 trip, no extra
- water < capacity (>0)      → ceil = 1 trip

## Contract
- Pure; does not mutate grid. Returns int.

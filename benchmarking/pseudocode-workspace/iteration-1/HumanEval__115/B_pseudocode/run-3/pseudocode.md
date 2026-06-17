# max_fill plan

Verdict: mostly simple aggregation, but the per-row "lowerings" is a ceiling-division
with an off-by-one trap (a row of all zeros must contribute 0, not 1). Plan the core.

## Data & invariants
- grid: list of rows, each row a list of 0/1. All rows same length.
- capacity: int, 1..10.
- For one row: water = count of 1s. Lowerings for that row = ceil(water / capacity).
  Invariant: empty/all-zero row contributes 0 (ceil(0/cap) = 0, not 1).
- Output: sum of per-row lowerings, an integer ≥ 0.

## Control flow
```
total ← 0
for each row in grid:
    water ← sum of row          # number of 1s
    total ← total + ceil(water / capacity)
return total
```

## Edge cases
- all-zero grid            → every row water=0 → ceil(0/cap)=0 → total 0  (Example 3)
- water exactly divisible  → e.g. 4 units, cap 2 → ceil = 2, no extra trip
- water not divisible      → e.g. 1 unit, cap 1 → 1; 3 units cap 2 → 2
- single row / single col  → handled by general loop

## Verify against examples
- Ex1 cap1: rows sum 1,1,4 → 1+1+4 = 6 ✓
- Ex2 cap2: rows sum 2,0,4,3 → 1+0+2+2 = 5 ✓
- Ex3 cap5: rows sum 0,0 → 0 ✓

## Contract
Pure; does not mutate grid; returns int.

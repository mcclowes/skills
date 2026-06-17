# max_fill plan

Verdict: logic task — per-row aggregation plus ceiling division. The bug risk is the
rounding-up (a floor would silently undercount), so plan the core.

## Data & invariants
- grid: list of rows; each row a list of 0/1. All rows same length (given).
- capacity: int >= 1.
- For one well with `w` units of water, lowerings needed = ceil(w / capacity).
  Invariant: a well with 0 water costs 0 (ceil(0/c) = 0, holds). A non-empty well
  always costs >= 1.

## Control flow
total <- 0
for each row in grid:
  w <- sum of row            # count of 1s
  total <- total + ceil(w / capacity)
return total

## Edge cases
- empty well (all 0s)        -> sum 0 -> ceil(0/c)=0, adds nothing
- all wells empty            -> total 0   (example 3)
- water exactly = capacity   -> 1 lowering, ceil exact, no extra
- water just over multiple   -> e.g. 4 units, cap 3 -> ceil = 2, not 1 (the key line)
- capacity 1                 -> lowerings == total water units (example 1: 6)

## Contract
Pure. Inputs not mutated. Returns int >= 0.

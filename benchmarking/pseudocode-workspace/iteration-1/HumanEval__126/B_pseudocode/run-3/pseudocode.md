# is_sorted — plan

Verdict: small but has a subtle invariant (the duplicate rule). Plan first.

## Data & invariants
- Input: list of non-negative integers.
- Output: boolean.
- Two independent conditions, both must hold for True:
  1. Ascending order: each element ≥ previous (non-strict — duplicates allowed up to a limit).
  2. No value appears more than twice. "More than 1 duplicate" = 3+ occurrences → False.
    - [1,2,2,3,3,4] → each appears ≤2 times → True
    - [1,2,2,2,3,4] → 2 appears 3 times → False

## Control flow
```
count occurrences of each value
if any value occurs ≥ 3 times → return False
for i from 1 to len-1:
  if lst[i] < lst[i-1] → return False   # strict <; equal is fine for ordering
return True
```

## Edge cases
- empty list        → no pairs, no counts ≥3 → True
- single element [5] → loop doesn't run, count is 1 → True
- exactly two dups [1,2,2,3] → count 2, allowed → True (if also ordered)
- unordered [1,3,2] → 2 < 3 fails → False

## Interface contract
- Pure; input not mutated; returns bool.

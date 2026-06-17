# make_a_pile

Mostly straight-line, but the step rule has a subtle invariant (parity preserved means each next level is just +2), so a quick plan.

## Data & invariants
- Input: positive integer n.
- Output: list of n integers, one per level.
- Invariant: level 0 = n; each subsequent level = previous + 2. Parity of n is preserved naturally, so "next odd if odd / next even if even" both reduce to "+2".

## Control flow
- result <- empty list
- for i from 0 to n-1:
    - append n + 2*i
- return result

## Edge cases
- n = 1 -> [1] (single element, loop runs once)
- n is given positive, so no zero/negative handling required.

## Interface contract
- Pure; returns new list of length n. No mutation of input (int is immutable anyway).

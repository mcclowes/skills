# make_a_pile

Verdict: near-trivial arithmetic sequence, but one subtle point (the step is +2 regardless of parity, because next-odd-after-odd and next-even-after-even both differ by 2). Brief plan.

## Data & invariants
- Input: positive integer n.
- Output: list of n integers, length == n, element i (0-based) == n + 2*i.
- Invariant: each level differs from the previous by exactly 2, preserving parity of n.

## Control flow
```
result ← empty list
for i from 0 to n-1:
    append (n + 2*i)
return result
```

## Edge cases
- n == 1 → [n], single level.
- n positive guaranteed → no zero/negative handling needed.

## Interface contract
- Pure function, returns new list of length n.

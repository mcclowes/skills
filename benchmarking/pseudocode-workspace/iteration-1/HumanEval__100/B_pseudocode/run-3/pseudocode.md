# make_a_pile

Verdict: near-trivial, but has a small accumulation loop with a parity subtlety worth a one-line plan.

Key insight: regardless of n's parity, the "next odd if odd / next even if even" rule
means each successive level simply adds 2 to the previous level. n and n+2 share parity.

Data & invariants:
  - Input: positive integer n.
  - Output: list of length n; element[i] = n + 2*i.
  - Invariant: every element shares parity with n; strictly increasing by 2.

Control flow:
  return [n + 2*i for i in 0..n-1]

Edge cases:
  - n = 1 -> [1]
  - n = 3 -> [3, 5, 7]
  - assume n >= 1 per spec (positive integer); n = 0 would give [] naturally.

Contract: pure; returns a new list.

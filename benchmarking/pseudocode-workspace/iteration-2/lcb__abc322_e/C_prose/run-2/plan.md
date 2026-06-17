# Plan

## Problem
We have K parameters (K ≤ 5), all starting at zero, and want every parameter to
reach at least P (P ≤ 5). There are N (≤ 100) development plans; plan i raises
parameter j by A[i][j] and costs C[i]. Each plan may be used at most once. Find
the minimum total cost to bring all K parameters to ≥ P, or -1 if impossible.

## Approach
This is a 0/1 knapsack over a multi-dimensional capped state. Since any value
above P is equivalent to exactly P (overshooting never helps and only matters
for hitting the target), we clamp each parameter's accumulated value at P. The
state is the tuple of current (clamped) parameter values, of which there are
(P+1)^K ≤ 6^5 = 7776 possible states.

## Algorithm
- Represent each state as a K-tuple of integers in [0, P].
- Maintain a dictionary `dp` mapping state -> minimum cost to reach it.
- Initialize dp = {(0,0,...,0): 0}.
- For each plan (cost c, gains a):
  - Iterate over a snapshot of current dp entries.
  - For each state, compute the new state by adding a[j] to each component and
    clamping at P.
  - Relax: if cost + c is lower than the stored cost for new_state, update it.
  - Using a snapshot per plan enforces the 0/1 constraint (each plan applied at
    most once per outer iteration).
- The answer is dp[(P,P,...,P)] if present, else -1.

## Edge cases
- A plan with all-zero gains: harmless, never reduces cost since c ≥ 1.
- Goal unreachable: target state never populated -> print -1.
- Clamping ensures large gains do not create out-of-range states.

## I/O contract
- Read N, K, P, then N lines each with C_i followed by K gains.
- Print the minimum cost integer, or -1.

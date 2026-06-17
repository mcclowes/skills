# Plan

## Problem restatement

We have K parameters, all starting at 0, and a target value P that each must reach
or exceed. There are N development plans; plan i has cost C_i and adds A_{i,j} to
parameter j. Each plan can be used at most once. Find the minimum total cost so every
parameter is at least P, or report -1 if impossible.

## Key observations

- K and P are tiny (each at most 5). Since any contribution beyond P is wasteful to
  track distinctly, we can cap each parameter's accumulated value at P. The state of
  progress is therefore a tuple of K values, each in [0, P], giving at most
  (P+1)^K <= 6^5 = 7776 reachable states.
- This is a multi-dimensional 0/1 knapsack: each plan is an item we either take or
  skip, and we want the minimum cost to reach the "full" state (P, P, ..., P).

## Algorithm

1. Parse N, K, P, then the N rows (cost plus K increments).
2. Maintain a DP dictionary mapping a state tuple to the minimum cost to reach it.
   Initialize with the all-zero state at cost 0.
3. For each plan, iterate over a snapshot of current states. For each state, compute
   the new state by adding the plan's increments componentwise, clamping each
   component to P. Update the new state's cost with min(existing, currentCost + C_i).
   Processing each plan against the snapshot enforces the use-at-most-once rule.
4. The answer is the cost stored for the full state (P, P, ..., P); if absent, -1.

## Edge cases

- A plan with all-zero increments: harmless, only ever raises cost, so it is never
  chosen for the optimum.
- Target unreachable even using all plans: full state never gets an entry; print -1.
- Costs up to 1e9 with up to 100 plans sum to <= 1e11, within Python's arbitrary ints.

## I/O contract

Input: first line "N K P"; next N lines each "C_i A_{i,1} ... A_{i,K}".
Output: single integer — the minimum total cost, or -1.

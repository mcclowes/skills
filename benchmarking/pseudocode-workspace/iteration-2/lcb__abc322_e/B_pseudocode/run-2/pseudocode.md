# Plan: minimum cost to raise all K params to at least P

Verdict: invariant-heavy DP over a capped multi-dimensional state. Planning first.

## Data & invariants
- N plans, K params (K,P ≤ 5), each plan i has cost C_i and vector A_i of K values.
- State = K-tuple of param totals, each capped at P (anything ≥ P is treated as exactly P,
  since reaching P is the goal and overshoot gives no benefit and keeps state space finite).
  Number of states = (P+1)^K ≤ 6^5 = 7776.
- dp[state] = minimum cost to reach that capped state using a subset of plans considered so far.
  Invariant: dp holds the optimum over the subset processed; each plan used at most once
  (achieved by 0/1-knapsack iteration — process plans one at a time, never revisit a plan).
- INF sentinel for unreachable states.

## Control flow
- Encode state as tuple of K ints in [0,P], or as base-(P+1) integer.
- dp ← all INF; dp[all-zero state] = 0.
- for each plan (C, A) in plans:                # 0/1 knapsack: outer = items
    new_dp ← copy of dp                          # option: skip this plan (carried by copy)
    for each state s with dp[s] < INF:
        s' ← cap(s + A) componentwise at P       # apply plan
        new_dp[s'] ← min(new_dp[s'], dp[s] + C)
    dp ← new_dp
  (Copy-then-update guarantees each plan contributes at most once per state — true 0/1.)
- answer ← dp[target] where target = all-P state.
- if answer == INF → print -1 else print answer.

## Edge cases & failure modes
- All-zero start already meets goal only if P==0, but P ≥ 1 by constraints, so start ≠ target generally.
- A_{i,j} can be 0 → plan may not advance some params; capping still correct.
- Capping is essential: without it states blow up and "≥ P" semantics break. Use min(total, P).
- Unreachable target (sample 2) → dp[target] stays INF → print -1.
- Costs up to 1e9, N up to 100 → max total 1e11, exceeds 32-bit but fine for Python ints.
- Must NOT reuse a plan: copy-then-update per plan enforces this. Mutating dp in place while
  iterating the same plan would allow reuse — avoided.

## Interface contract
- Read from stdin, print single integer (min cost) or -1 to stdout.
- Pure computation; no mutation of input beyond local dp arrays.

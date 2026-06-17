# Plan: minimum cost to raise all K parameters to ≥ P

Verdict: logic-heavy (DP over bounded multidimensional state, value clamping). Plan first.

## Data & invariants
- N plans, each: cost C_i, contribution vector A_i of length K (each 0..P).
- State = tuple of K current parameter values, each clamped to [0, P]
  (values above P are useless, so cap at P to keep state space finite).
- State space size = (P+1)^K ≤ 6^5 = 7776.
- dp[state] = minimum cost to reach that clamped state, considering plans processed so far.
  Invariant: dp holds the best cost using a subset of the plans already iterated; each plan
  used at most once because we process plans one at a time (0/1 knapsack style).
- Goal state = (P, P, ..., P) i.e. every parameter clamped to P (since ≥P clamps to P).

## Control flow
- INF = large sentinel (e.g. infinity).
- dp ← map from state → cost; init dp[(0,...,0)] = 0, all others INF.
- for each plan (C, A):
    new_dp ← copy of dp                       # option: don't take this plan
    for each state s with dp[s] < INF:
        ns ← elementwise min(s[j] + A[j], P) for each j   # apply plan, clamp at P
        cand ← dp[s] + C
        if cand < new_dp[ns]: new_dp[ns] = cand
    dp ← new_dp
  # iterate over the OLD dp (snapshot) so each plan applied at most once per item.
- answer = dp[(P,...,P)]; if INF → -1 else that value.

## Edge cases & failure modes
- All A_i zero / insufficient total: goal state never reached → dp[goal] = INF → print -1.
- P could be reached/exceeded: clamp ensures (P,...,P) is the unique "done" bucket.
- Cost overflow: C_i ≤ 1e9, N ≤ 100 → max sum ≤ 1e11, fits in Python int (no overflow concern).
- Single plan that alone reaches goal → handled by the per-plan update.
- Must snapshot dp before applying a plan (copy), else a plan could be used twice within one step.

## Interface contract
- Input: first line "N K P", then N lines "C A_1 ... A_K".
- Output: single integer = min total cost, or -1 if unreachable.
- Pure computation; reads stdin, writes stdout.

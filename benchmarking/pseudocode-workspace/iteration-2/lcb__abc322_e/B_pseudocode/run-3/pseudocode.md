# Plan: minimum cost to raise all K parameters to ≥ P

Verdict: logic-heavy — multidimensional bounded knapsack DP with state capping. Plan first.

## Data & invariants
- N plans, each: cost C_i ≥ 1, gains A_i = (a_1..a_K), each 0..P.
- K, P ≤ 5. State = K-tuple of "progress so far", each component capped at P
  (anything ≥ P counts as P; no benefit to exceeding the target).
- dp[state] = minimum total cost to reach exactly that capped state.
  Number of states = (P+1)^K ≤ 6^5 = 7776. Tiny.
- Invariant: dp holds the best cost using a subset of the plans already processed.
  Each plan used at most once → process plans one at a time (0/1 knapsack ordering),
  and within a plan iterate states without reusing the same plan twice.

## Control flow
- Encode state as base-(P+1) integer over K components, or as a tuple.
- INF = large sentinel (e.g. float inf or a big int).
- dp ← all INF; dp[zero-state] = 0.
- for each plan (C, A) in plans:
    new_dp ← copy of dp        # represents "not taking this plan"
    for each state s with dp[s] < INF:
        next = for each component j: min(P, s_j + A_j)   # cap at P
        cand = dp[s] + C
        if cand < new_dp[next]: new_dp[next] = cand
    dp ← new_dp
  (Copy-then-update ensures each plan used at most once: updates read from old dp.)
- Answer = dp[full-state] where full-state has all components = P.
- If answer == INF → print -1 else print answer.

## Edge cases & failure modes
- A plan with all-zero gains but positive cost: never helps reach target, naturally
  ignored because it doesn't reduce dp at the goal (taking it only adds cost).
- P could be reached only by exceeding individual targets → capping handles it
  (extra gain beyond P collapses to same goal state).
- No combination reaches all-P → dp[goal] stays INF → output -1 (sample 2).
- Costs up to 1e9, N up to 100 → max total 1e11, exceeds 32-bit but Python ints fine.
- Zero plans taken gives zero-state; goal only reachable if P==0, but P≥1 so need plans.

## Interface contract
- Read "N K P" then N lines "C A_1..A_K" from stdin.
- Print single integer: min cost, or -1 if unreachable.

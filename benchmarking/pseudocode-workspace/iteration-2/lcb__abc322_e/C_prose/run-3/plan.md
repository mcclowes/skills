# Plan

## Problem restatement
We have K parameters (K up to 5), all starting at 0, and a target P (up to 5) for each.
There are N (up to 100) development plans. Plan i has cost C_i and contributes A_{i,j} to
parameter j. Each plan may be used at most once. Find the minimum total cost so that every
parameter reaches at least P, or -1 if impossible.

## Key observation
Because each parameter only needs to reach P, any contribution above P is wasted. So we can
cap the "state" of each parameter at P. The state is a tuple of K values, each in [0, P].
The number of distinct states is (P+1)^K, which is at most 6^5 = 7776. This is small.

## Algorithm: 0/1 knapsack over capped multidimensional states
- Represent the DP as a dictionary (or array indexed by encoded state) mapping each reachable
  state tuple -> minimum cost to reach that state.
- Initialize dp[(0,0,...,0)] = 0.
- For each plan i (processed once, giving 0/1 semantics):
  - Build a fresh next-DP starting as a copy of the current dp (the "don't take plan i" option).
  - For every state s in the current dp with cost c, compute the new state by adding A_{i,j} to
    each coordinate and capping at P: ns_j = min(s_j + A_{i,j}, P).
  - Relax: if c + C_i < next_dp[ns], update it.
  - Replace dp with next_dp. Iterating over the *old* dp (not next_dp) ensures each plan is used
    at most once (standard 0/1 knapsack ordering).
- The goal state is (P, P, ..., P). Answer = dp[goal] if present, else -1.

## Edge cases
- A plan contributing 0 to everything is allowed (cost still added if taken; never beneficial).
- Capping handles A_{i,j} possibly summing well beyond P.
- If goal unreachable even using all plans, print -1.
- Costs up to 1e9 with up to 100 plans -> max total 1e11, fits in Python int trivially.

## I/O contract
Input: first line "N K P"; then N lines each "C_i A_{i,1} ... A_{i,K}".
Output: single integer — minimum total cost, or -1.

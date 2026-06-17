# abc323_e — probability song 1 plays at X+0.5

Verdict: probability DP + modular inverse. Logic-heavy (boundary on time window,
inclusive/exclusive endpoints), planning first.

## Data & invariants
- N songs, durations T[1..N], all integer ≥ 1. X integer ≥ 0. MOD = 998244353.
- inv_N = modular inverse of N (the per-choice probability 1/N).
- dp[t] for t in 0..X = probability that *some song boundary* (a song starts)
  exactly at integer time t. Boundaries only occur at integer times since all
  T_i integer and start time 0.
  Invariant: dp[0] = 1 (a song starts at time 0 with certainty).
  dp[t] = sum over songs i of dp[t - T[i]] * inv_N, for t - T[i] >= 0.
  (Renewal recurrence: a boundary at t happens iff a boundary at t-T[i] occurred
   and song i was chosen there, for some i.)

## Why X+0.5
- We need song 1 actively playing at real time X+0.5 (never on a boundary, since
  +0.5 avoids integer instants — no ambiguity).
- Song 1 is playing at X+0.5 iff there is a start time s (integer, 0..X) where:
    * a boundary occurs at s            -> weight dp[s]
    * song 1 is the chosen song there   -> factor inv_N
    * song 1 still running at X+0.5: s <= X+0.5 < s + T[1]
      => s <= X (since s integer, s <= X+0.5 means s <= X)
      => X+0.5 < s + T[1]  =>  s > X+0.5 - T[1]  =>  s >= X - T[1] + 1
        (s integer, X+0.5 - T[1] = X - T[1] + 0.5, so s >= ceil = X-T[1]+1)
  So s ranges over [max(0, X - T[1] + 1), X], inclusive both ends.

## Control flow
  inv_N = pow(N, MOD-2, MOD)
  dp = array size X+1, all 0
  dp[0] = 1
  for t from 1 to X:
    for each duration d in T:
      if t - d >= 0:
        dp[t] += dp[t-d] * inv_N   (mod)
  answer = 0
  lo = max(0, X - T[1] + 1)
  for s from lo to X:
    answer += dp[s] * inv_N        (mod)   # song 1 chosen at boundary s
  print answer

## Edge cases
- X = 0: only s = 0 possible (lo = max(0, 1-T1+1)=max(0,2-T1) which is 0 when
  T1>=2, but could be... 2-T1: if T1=1 ->1, T1>=2 ->0). dp[0]=1, contributes inv_N
  for each valid s. Sample2: X=0,T1=1 -> lo=max(0,0)=0, s=0 only, ans=inv_5=1/5. OK.
- T[1] > X: lo = max(0, X-T1+1) clamps to 0, full range 0..X considered.
- t-d could land on dp index 0 (boundary at 0) — included, correct.
- All arithmetic mod MOD; inv_N as modular inverse, not float.

## Interface contract
- Read "N X" then N integers. Print single integer z in [0, MOD-1].
- Pure computation; deterministic.

## Sanity vs sample 1: N=3,X=6,T=[3,5,6].
- dp via recurrence; answer = sum_{s in [6-3+1=4 .. 6]} dp[s]*inv_3.
  Expected 7/27. Trust recurrence.

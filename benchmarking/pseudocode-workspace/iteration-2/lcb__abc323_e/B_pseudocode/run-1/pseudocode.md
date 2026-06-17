# ABC323 E — Song 1 playing at time X+0.5

Verdict: probability DP with modular inverse. Logic-heavy (DP recurrence, boundary,
modular arithmetic). Planning first.

## Data & invariants
- N songs, durations T[1..N]. MOD = 998244353.
- invN = modular inverse of N (each song chosen with prob 1/N).
- dp[t] = probability that some song *starts* exactly at time t (a song boundary
  occurs at t). Time measured in integer seconds (all T_i integers, and X+0.5 means
  we look at the half-open interval — only integer start times matter).
  Invariant: dp[0] = 1 (a song starts at time 0). dp[t] for t>0 is sum over
  predecessors.

## Key insight
Song 1 is playing at time X+0.5 iff song 1 *started* at some integer time t with
  t <= X+0.5 < t + T[1]   i.e.   t <= X  and  t + T[1] >= X+1
  => t in [X - T[1] + 1, X], and a boundary (any song's start) occurs at t AND the
  song chosen at t is song 1.
Equivalently: P = sum over t in [max(0, X-T1+1) .. X] of dp[t] * invN
where dp[t] = probability a song-boundary lands exactly at time t.

dp boundary recurrence:
  dp[0] = 1
  dp[t] = sum_{i=1..N} dp[t - T[i]] * invN    for t >= 1, where t - T[i] >= 0
Because to have a boundary at t, the previous song started at t - T[i] (prob dp[t-T[i]])
and that previous song was song i (prob 1/N), and it ended exactly at t.

## Control flow
1. read N, X, T[1..N]; MOD=998244353; invN = pow(N, MOD-2, MOD)
2. dp = array size (X+1), all 0. dp[0] = 1.
3. for t from 1 to X:
     acc = 0
     for i in 1..N:
       if t - T[i] >= 0: acc += dp[t - T[i]]
     dp[t] = acc * invN mod MOD
4. answer = sum of dp[t] for t in [lo .. X] * invN mod MOD,
     where lo = max(0, X - T[1] + 1)
5. print answer

## Edge cases
- X = 0: lo = max(0, 1-T1) = 0 (T1>=1). Window = {0}. dp[0]=1.
  answer = dp[0]*invN = 1/N. Matches sample 2 (1/5).
- T[1] > X: lo clamps to 0, full window [0..X].
- X large (1e4), N up to 1e3: dp loop is X*N = 1e7, fine.

## Contract
Input via stdin, output single integer (z in [0, MOD-1]) to stdout.

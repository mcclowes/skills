# Plan: probability song 1 is playing at time X+0.5

Verdict: numerical/modular DP with subtle boundary conditions — plan first.

## Problem restated
Random play: at each step pick a uniform-random song (1/N each), play to end.
Want P(song 1 is the song playing at time t = X+0.5), mod p = 998244353.

Song 1 is playing at time X+0.5 iff some song *starts* at an integer-ish boundary s
such that s ≤ X+0.5 < s + T_1, and that started song is song 1, AND a song boundary
(start of a play) occurs exactly at time s where s is the cumulative sum of some sequence
of chosen song lengths.

Key reformulation:
- Let f(s) = probability that some song *starts* exactly at time s (i.e. s is reachable
  as a sum of chosen song durations, weighting each chosen song by 1/N).
- Song 1 is playing at X+0.5 iff song 1 started at some time s with
  s ≤ X+0.5 < s+T_1, i.e. s ≤ X (since s integer, s ≤ X+0.5 means s ≤ X)
  and s + T_1 > X+0.5, i.e. s + T_1 ≥ X+1, i.e. s ≥ X+1-T_1.
  So s in [X+1-T_1, X], integer.
- Probability song 1 starts at s = f(s) * (1/N).
- Answer = sum over valid s of f(s) * (1/N).

## Data & invariants
- dp[t] = probability that a song-start (play boundary) occurs exactly at time t.
  dp[0] = 1 (a song starts at time 0 with probability 1).
- Invariant: dp[t] = (1/N) * sum over songs i of dp[t - T_i]   for t ≥ 1.
  (To start a song at t, the previous song started at t - T_i and was song i.)
- We only need dp[t] for t in [0, X] (since valid start s ≤ X ≤ 10^4).
- Modular: all values in Z/p. 1/N = modular inverse of N.

## Control flow
```
read N, X, T[1..N]
p = 998244353
invN = modpow(N, p-2, p)

dp = array size X+1, all 0
dp[0] = 1
for t from 1 to X:
    acc = 0
    for each song i:
        if t - T[i] >= 0:
            acc += dp[t - T[i]]
    dp[t] = acc * invN mod p

answer = 0
lo = max(0, X + 1 - T[1])     # smallest valid start
for s from lo to X:
    answer += dp[s] * invN     # prob song1 started at s = dp[s] * (1/N)
answer mod p
print answer
```

## Edge cases
- X = 0: dp array is just [1]. Valid s range: lo = max(0, 1 - T[1]) = 0 (since T_1≥1),
  hi = 0. answer = dp[0]*invN = 1/N. Matches sample 2 (1/5).
- T_1 > X: lo = max(0, X+1-T_1) could be 0; range [0, X] all valid since song1
  started anytime in [0,X] still playing at X+0.5 (it's long enough). Correct.
- T_1 ≤ X: only recent starts count; lo clamps to X+1-T_1.
- s = X+0.5 boundary: a song that *ends* exactly at integer time s' has the next song
  starting at s'. At time X+0.5 (strictly between integers), the playing song is the
  one that started at the largest integer ≤ X+0.5, i.e. ≤ X. Using s ≤ X (strict via .5)
  and s+T_1 ≥ X+1 (i.e. song still going at X+0.5) is correct — no double counting at
  exact integer boundaries because X+0.5 is never an integer.

## Interface contract
- Input: stdin "N X" then N integers T_i.
- Output: single integer z in [0, p-1].
- Pure arithmetic mod p; uses Fermat inverse (p prime, N < p so invertible).

## Sample check (sample 1: N=3, X=6, T=[3,5,6])
dp[0]=1.
dp[1]=0, dp[2]=0.
dp[3]=(dp[0])*1/3 = 1/3  (only T=3 reaches).
dp[5]=(dp[0]) *1/3 = 1/3 (T=5).
dp[6]=(dp[3]+dp[0])*1/3? T=[3,5,6]: dp[6-3]+dp[6-5]+dp[6-6]=dp[3]+dp[1]+dp[0]=1/3+0+1=4/3, *1/3=4/9.
T_1=3, lo=max(0,7-3)=4, hi=6. valid s in {4,5,6}.
dp[4]=dp[1]+...=0. dp[5]=1/3. dp[6]=4/9.
sum = (0 + 1/3 + 4/9)*1/3 = (3/9+4/9)/3 = (7/9)/3 = 7/27. Matches 7/27. ✓

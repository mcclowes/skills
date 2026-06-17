# Plan

## Problem
Songs are chosen uniformly at random (probability 1/N each), played to completion,
then another is chosen, repeating. We want the probability that song 1 is playing at
time X + 0.5 seconds.

## Key observation
Song 1 is playing at time X + 0.5 if and only if some song *starts* at a time t such
that that song is song 1 and t <= X + 0.5 < t + T_1, i.e. the start of a play of song 1
occurs at an integer time t with X - T_1 + 1 <= t <= X (since starts only happen at
integer boundaries, because all T_i are integers and time 0 is a start). More precisely
song 1 covers the moment X+0.5 iff a play of song 1 begins at some boundary time
t in {X - T_1 + 1, ..., X} and that play is song 1.

## DP
Let dp[t] = probability that some song *finishes* exactly at time t (equivalently a new
song boundary occurs at time t), for t = 0..X. dp[0] = 1 (a boundary at time 0).
Transition: from a boundary at time t, with prob 1/N we play song j of length T_j, which
creates a new boundary at t + T_j. So:
  dp[t + T_j] += dp[t] * (1/N)  for each j, when t + T_j <= X.

We only need boundaries up to time X (a song starting after X cannot be the song 1 play
covering X+0.5 except one starting at t <= X). Actually we cap at t <= X.

## Answer
For each boundary time t with X - T_1 + 1 <= t <= X (and t >= 0), the probability that a
song-1 play begins there is dp[t] * (1/N). Sum these:
  answer = sum_{t = max(0, X-T_1+1)}^{X} dp[t] * (1/N).

The play of song 1 starting at t covers [t, t+T_1), which includes X+0.5 iff
t <= X+0.5 < t+T_1, i.e. t <= X and t > X+0.5-T_1 => t >= X-T_1+1 (integers).

## Modular arithmetic
All probabilities computed mod 998244353. 1/N = modular inverse of N. Use pow(N, MOD-2).

## Edge cases
- X = 0: only t = 0 boundary in range (if T_1 >= 1, X-T_1+1 <= 0), answer = dp[0]*inv = 1/N.
- T_1 large: lower bound clamped to 0.
- dp array size X+1.

## I/O
Read N, X then N integers. Print single integer answer mod 998244353.

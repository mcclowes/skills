# Plan: probability song 1 is playing at time X+0.5

## Input/output contract
- Read `N X` then `N` integers `T_1..T_N`.
- Output a single integer: the probability that song 1 is playing at time `X+0.5`, taken modulo `M = 998244353`.

## Core idea
Time `X+0.5` is non-integer, so it falls strictly inside some song. Song 1 is playing at `X+0.5` iff a play of song 1 *starts* at some integer second `s` with `s <= X` and `s + T_1 > X`, i.e. `s` in the range `(X - T_1, X]`, equivalently `X - T_1 + 1 <= s <= X`.

Because every song boundary lands on an integer second, the relevant start times are integers. Let `dp[t]` = probability that some song *starts* exactly at time `t` (a boundary occurs at `t`). A boundary occurs at time 0 (the first song starts), so `dp[0] = 1`. Each chosen song has probability `1/N`. Then a boundary at `t` produces a boundary at `t + T_i` with probability `(1/N)` for each song `i`:
`dp[t + T_i] += dp[t] * inv(N)`.

The probability that song 1 is playing at `X+0.5` is the probability that song 1 starts at some boundary `s` with `X - T_1 + 1 <= s <= X`:
`answer = sum over s in [max(0, X-T_1+1) .. X] of dp[s] * inv(N)`
(the `inv(N)` is the chance the song started at `s` is specifically song 1).

## Algorithm steps
1. `invN = modpow(N, M-2, M)`.
2. `dp` array of size `X+1`, `dp[0]=1`.
3. For `t` from 0 to X: for each song length `T_i`, if `t+T_i <= X`, add `dp[t]*invN` to `dp[t+T_i]`.
4. `ans = sum dp[s]*invN` for `s` in `[max(0,X-T_1+1), X]`.

## Complexity
O(N * X) ~ 10^3 * 10^4 = 10^7, fine.

## Edge cases
- `X=0`: start time must be `s=0`, answer is `dp[0]*invN = 1/N`.
- `T_1 > X`: lower bound clamps to 0.
- All arithmetic mod M.

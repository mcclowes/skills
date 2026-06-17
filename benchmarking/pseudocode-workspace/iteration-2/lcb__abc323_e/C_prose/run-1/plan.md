# Plan

## Input/output contract
Read `N X` then a line of `N` integers `T_1..T_N`. Output a single integer: the
probability that song 1 is playing at time `X + 0.5`, expressed modulo
`MOD = 998244353` (i.e. `y * inverse(x) mod MOD` for the irreducible fraction).

## Core idea
Model the process by the discrete time at which a song *starts*. A song boundary
can only occur at an integer time, because all `T_i` are integers and the first
song starts at time 0. Let `start[t]` be the probability that some song begins
playing exactly at integer time `t`.

- `start[0] = 1` (random play begins at time 0).
- For `t >= 1`: `start[t] = sum_i start[t - T_i] * (1/N)`, since the previous
  song (length `T_i`, chosen with probability `1/N`) must have started at
  `t - T_i` and ended exactly at `t`.

This is a DP over `t = 0..X`. With `N <= 1000` and `X <= 10^4`, the cost is
`O(N * X) <= 10^7` modular operations, which is fine.

## Answer
Song 1 is playing at time `X + 0.5` iff song 1 started at some integer time `t`
with `t <= X` (it has started by `X+0.5`) and `t + T_1 > X + 0.5`, i.e.
`t > X + 0.5 - T_1`. Since `t` is an integer, this means
`X - T_1 + 1 <= t <= X`. The probability song 1 starts at `t` is
`start[t] * (1/N)`. So the answer is `(1/N) * sum_{t=max(0, X-T_1+1)}^{X} start[t]`.

## Edge cases
- `X - T_1 + 1` may be negative -> clamp the lower bound to 0.
- `t = 0` is included when `T_1 > X` (sample 2: X=0, the first song still plays).
- All arithmetic done modulo MOD using `pow(N, MOD-2, MOD)` for `1/N`.

## Modular details
MOD is prime, so inverses via Fermat's little theorem. Accumulate `start[]` as
ints mod MOD; multiply the final sum by `invN` once.

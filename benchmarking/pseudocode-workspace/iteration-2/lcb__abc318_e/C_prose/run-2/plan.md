# Plan

## Input/output contract
- Read `N` from the first line, then `N` integers `A_1..A_N` from the second line.
- Print a single integer: the number of triples `(i, j, k)` with `1 <= i < j < k <= N`, `A_i = A_k`, and `A_i != A_j`.

## Core idea
For any fixed value `v`, consider all positions where `v` occurs. Pick a pair of those positions to serve as `(i, k)` with `i < k` (both equal to `v`). The middle index `j` ranges over `i < j < k`, giving `(k - i - 1)` candidate positions. Among those middle positions we must exclude any `j` where `A_j = v`, because we require `A_i != A_j`.

So the answer is the sum over all valid triples of:
`(number of indices strictly between i and k) - (number of those indices that also equal v)`.

## Avoiding O(N^2) per value
Two contributions, computed separately:

1. Total "gap" sum: over all ordered pairs `i < k` of equal-valued positions, sum `(k - i - 1)`. Iterate positions left to right; maintain for each value the count of earlier occurrences `cnt[v]` and the sum of their indices `sumIdx[v]`. When we reach position `k` (1-based) with value `v`, the pairs ending here contribute `cnt[v]*k - sumIdx[v] - cnt[v]` to the gap total (the `- cnt[v]` accounts for the `-1` per pair). Then update `cnt[v] += 1`, `sumIdx[v] += k`.

2. Subtract triples where the middle equals `v`. For three equal-valued positions `p_a < p_b < p_c` (all value `v`), the middle being equal is one bad triple. Count, per value with `m` occurrences, the number of ordered triples = `C(m, 3)`. Sum over values and subtract.

## Edge cases
- Values appearing fewer than twice contribute nothing.
- Large N (3e5): all sums fit in Python ints; algorithm is O(N).
- Reading input robustly via split (bytes compared directly, no need to convert to int).

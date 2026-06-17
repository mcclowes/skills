# Plan

## Problem
Count triples (i, j, k) with i < j < k where A_i = A_k and A_i != A_j.

## Approach
For a fixed pair (i, k) with i < k and A_i = A_k, the valid middle indices j are
those strictly between i and k (so there are k - i - 1 candidate positions). Among
those candidates we must exclude any j where A_j equals A_i (= A_k). Counting per
pair would be O(N^2), too slow for N up to 3*10^5.

Instead, group positions by value. For each value v, consider its sorted list of
positions p_0 < p_1 < ... < p_{m-1}. The endpoints i and k of a valid pair must
both have value v. For a pair (p_a, p_b) with a < b, the number of candidate j
positions strictly between them is (p_b - p_a - 1). Among those candidates, the
ones to exclude are the positions of value v that lie strictly between p_a and p_b,
which is exactly (b - a - 1) positions. So the valid j count for this pair is
(p_b - p_a - 1) - (b - a - 1) = p_b - p_a - b + a.

Total answer = sum over all values v, over all pairs a < b in v's position list, of
(p_b - p_a - b + a).

## Efficient summation
For each value, split the per-pair term into two parts summed over pairs a<b:
- sum of (p_b - p_a): for each b, p_b contributes +p_b for each a<b (b times) and
  for each a, -p_a contributed by later b's. Standard prefix-sum: iterate b, keep
  running sum of previous positions; add p_b*b - (prefix sum of p_0..p_{b-1}).
- sum of (a - b) = -(b - a): similarly handled with indices.

Combine: for pair (a,b) term = (p_b - b) - (p_a - a). Define q_x = p_x - x. Then
term = q_b - q_a, summed over a < b. For a sorted list, sum_{a<b}(q_b - q_a) =
sum_b q_b * b - prefix, computed in one pass: maintain prefix sum S of q values;
for each new q_b add q_b * (count_so_far) - S.

## Complexity
O(N) total across all values. Use Python ints (arbitrary precision, no overflow).

## I/O contract
Input: line 1 = N; line 2 = N integers. Output: single integer (the count).

## Edge cases
- Values appearing fewer than 2 times contribute 0.
- N = 3 minimal case.
- Answer can be large; Python ints handle it.

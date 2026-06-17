# Plan

## Problem
Given N strings S_1..S_N and a target string T, count the number of ordered pairs
(i, j) such that the concatenation S_i + S_j contains T as a (not necessarily
contiguous) subsequence.

## Key idea
T is a subsequence of S_i + S_j iff there exists a split point k (0 <= k <= |T|)
such that the prefix T[0:k] is a subsequence of S_i AND the suffix T[k:] is a
subsequence of S_j. The greedy matching is monotone, so it suffices to compute,
per string:

- `pref(S)`: the largest number of leading characters of T that can be matched
  greedily as a subsequence of S, scanning T from the front.
- `suf(S)`: the largest number of trailing characters of T that can be matched
  greedily as a subsequence of S, scanning T from the back.

Then the pair (i, j) is valid iff `pref(S_i) + suf(S_j) >= |T|`. Reason: S_i can
cover the first `pref(S_i)` characters of T, and S_j can cover the last
`suf(S_j)` characters; if together they reach or exceed |T|, the whole T is
covered (the greedy front match is a longest matchable prefix, so any split
within range works).

## Algorithm steps
1. Read N, T, and the N strings.
2. For each S_i compute a_i = pref(S_i) and b_i = suf(S_i) via two-pointer greedy.
3. Let m = |T|. Build a sorted array of all b_j values.
4. For each a_i, count the number of j with b_j >= m - a_i using binary search
   (bisect_left on the sorted b array). Sum these counts.
5. Print the total.

## Edge cases
- If a_i >= m, every j qualifies (m - a_i <= 0, and all b_j >= 0). Handled
  naturally since b_j >= 0 always.
- T longer than any reasonable single string: pairs may still work via the split.
- Pairs (i, i) are allowed and counted.
- Single string (N=1): only the (1,1) pair considered.

## I/O contract
Input: first line "N T"; next N lines the strings. Output: single integer, the
count. Total input length up to ~5e5, so use fast sys.stdin reading and an O(L)
greedy plus O(N log N) counting.

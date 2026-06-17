# Plan

## Problem
Given N strings S_i and a target T, count ordered pairs (i, j) such that the
concatenation S_i + S_j contains T as a (not necessarily contiguous)
subsequence.

## Key insight
For a single string S, define `prefix(S)` = the largest k such that the first k
characters of T form a subsequence of S (greedy match of T from the left). Walk
through S, advancing a pointer into T whenever characters match.

Symmetrically, define `suffix(S)` = the largest m such that the last m
characters of T form a subsequence of S (greedy match of T from the right).

The concatenation S_i + S_j contains T as a subsequence iff we can split T into
a prefix consumed by S_i and the remaining suffix consumed by S_j. Greedily,
S_i can cover the first `a = prefix(S_i)` characters of T, and S_j can cover the
last `b = suffix(S_j)` characters of T. The pair works iff `a + b >= len(T)`,
i.e. S_i covers a prefix and S_j covers a suffix that together overlap or meet.

Why greedy split is sufficient: subsequence matching is monotone. If S_i can
match the first a chars and S_j the last b chars with a + b >= L, the prefix
[0, a) and suffix [L-b, L) cover all of T, so the full T is a subsequence of the
concatenation. Conversely if a + b < L there is a gap that neither can fill.

## Algorithm
1. Read N, T, and all S_i.
2. For each S_i compute a_i = prefix(S_i) and b_i = suffix(S_i).
3. Let L = len(T). Count pairs (i, j) with a_i + b_j >= L.
   - Build a sorted array of all b_j values.
   - For each a_i, the number of valid j is the count of b_j >= L - a_i.
   - Use a frequency/suffix-count over b values (b in [0, L]) for O(N + L), or
     binary search on the sorted b array for O(N log N).

## Edge cases
- a_i can equal L (S_i alone contains T) → any j works.
- L - a_i <= 0 → all N values of b qualify.
- Single string, T not a subsequence of S+S → answer 0.
- Large inputs: total length up to 5e5, N up to 5e5. Use fast I/O and O(L)
  counting buckets indexed 0..L.

## I/O contract
Input: first line "N T", then N lines each one S_i. Output: single integer, the
count of valid ordered pairs.

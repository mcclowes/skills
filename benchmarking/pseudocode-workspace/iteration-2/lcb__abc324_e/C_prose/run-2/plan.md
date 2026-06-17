# Plan

## Problem restated

Given N strings and a target T, count ordered pairs (i, j) such that the
concatenation S_i + S_j contains T as a (not necessarily contiguous)
subsequence. Both i and j range over 1..N, and i may equal j, giving N^2
candidate pairs.

## Key observation

If we walk T greedily against a single string, the natural quantities are:

- `pre[i]` = the length of the longest *prefix* of T that S_i contains as a
  subsequence. Equivalently, after greedily matching T from the front against
  S_i, how many characters of T were consumed.
- `suf[i]` = the length of the longest *suffix* of T that S_i contains as a
  subsequence. Compute by greedily matching T from the back against S_i read
  from the back.

For a concatenation S_i + S_j to contain T as a subsequence, we can split T at
some position: the first part is matched inside S_i and the remainder inside
S_j. Greedy matching is optimal, so the best split is to let S_i absorb as much
of T's prefix as possible (`pre[i]`) and S_j absorb T's suffix. The pair
succeeds iff `pre[i] + suf[j] >= len(T)`. (If S_i alone already contains all of
T, then pre[i] = len(T) and the condition holds for every j.)

## Algorithm

1. Read N, T, and all strings.
2. For each string compute pre and suf via greedy two-pointer scans (O(len)).
3. Let m = len(T). We need pairs with pre[i] + suf[j] >= m, i.e.
   suf[j] >= m - pre[i]. Build a frequency/count array over suf values
   (0..m), take a suffix-sum so `atleast[k]` = number of j with suf[j] >= k.
4. For each i, add `atleast[max(0, m - pre[i])]` to the answer.
5. Print the total (use Python big ints; answer can reach N^2 = 2.5e11).

## Edge cases

- pre[i] >= m means need suf[j] >= 0, i.e. all N values of j count.
- m - pre[i] could exceed m only if pre negative (impossible); clamp index.
- Total string length up to 5e5, so all scans are linear overall. Use fast IO.

## I/O contract

Input: first line "N T"; then N lines each a string S_i. Output: single
integer, the count of valid pairs.

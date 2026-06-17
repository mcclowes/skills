# Plan

## Problem restatement
Given a digit string S of length N (1 <= N <= 13), count how many distinct
square numbers can be formed by permuting the digits of S and reading the
result as a base-10 integer. Permutations producing the same numeric value
count once (we count distinct square *numbers*, not permutations).

## Key observations
- N <= 13, so the value fits comfortably in a 64-bit integer (max ~10^13).
- Brute-forcing all 13! ≈ 6.2 billion permutations is too slow, but the digit
  *multiset* is what matters: many permutations share the same multiset
  arrangement. Better: iterate over candidate squares.
- Total numeric range is [0, 10^N). A number is achievable iff its decimal
  representation, **padded with leading zeros to exactly N digits**, has the
  same digit multiset as S. Leading zeros matter: e.g. "010" can form 1
  (value 1, padded to "001" -> digits {0,0,1} matches S's multiset).

## Algorithm (enumerate squares)
1. Read N and S. Compute the sorted digit-count signature of S (a tuple of 10
   counts, or sorted string of its digits).
2. Iterate k from 0 while k*k < 10^N. For each square v = k*k:
   - Format v as a string zero-padded to width N.
   - If that string's digit multiset equals S's multiset, count it.
3. Print the count.

The number of squares below 10^13 is about sqrt(10^13) ≈ 3.16 million — fast.
Each check is O(N). Total well within limits.

## Edge cases
- Leading zeros: padding to width N handles the "001" = 1 case correctly.
- N = 1: single digit; squares 0..9 padded to width 1; e.g. "0"->0 counts.
- Duplicate digits: multiset comparison naturally deduplicates values, and
  distinct squares are counted once since we iterate over k (distinct values).
- v = 0 (k = 0): allowed, padded string is "0...0".

## I/O contract
- Input: line 1 = N, line 2 = S.
- Output: single integer (count of distinct achievable square numbers).

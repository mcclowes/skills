# Plan

## Problem
Given a digit string S of length N (N up to 13), count how many distinct square
numbers can be formed by interpreting some permutation of the digits of S as a
decimal integer. Permutations that yield the same numeric value count once.

## Key insight
N is at most 13, so there are at most 13! permutations — too many to enumerate
directly when there are repeated digits, but more importantly we want distinct
values. A square number formed from a permutation has at most 13 digits, so its
value is below 10^13. Its square root is below ~3.17 million (sqrt(10^13) ≈
3,162,277). So instead of permuting, we iterate over every candidate square
x = k^2 for k from 0 up to floor(sqrt(10^13)), and check whether x's digits
(zero-padded to exactly N digits) form a multiset equal to the multiset of S's
digits. Leading zeros are naturally handled: a number like 1 with N=3 is "001",
which uses digits {0,0,1} — exactly a permutation of S if S has those digits.

## Algorithm
1. Read N and S.
2. Compute the target digit-count signature: a tuple/list of counts for digits 0..9 in S.
3. Determine upper bound: the largest value with N digits is 10^N - 1. Let
   limit = isqrt(10^N - 1).
4. For k from 0 to limit, let x = k*k. Format x as an N-character zero-padded
   string (x < 10^N guaranteed). Count its digit frequencies and compare to the
   target signature. If equal, increment the answer.
5. Print the answer.

Each square maps to a unique value, so distinctness is automatic — we never
double-count the same number.

## Edge cases
- N = 1: squares 0,1,4,9 etc.; single digit handled by padding (no-op).
- All zeros (e.g. "00"): only 0 (="00") matches → answer 1.
- Repeated digits: comparing multisets, not positions, so duplicates handled.
- Leading-zero permutations: zero-padding the square to N digits makes the
  comparison correct (e.g. "010" with N=3 matches square 1 → "001", and 100).

## I/O contract
Input: line 1 = N, line 2 = S. Output: single integer count.

## Complexity
~3.2M iterations, each O(N) work. Fast enough in Python within limits.

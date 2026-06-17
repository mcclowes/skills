# Plan: count distinct square numbers from permutations of digits

## Input/output contract
- Input: line 1 is `N` (1 ≤ N ≤ 13); line 2 is string `S` of `N` digits.
- Output: a single integer, the count of distinct square numbers obtainable by
  permuting the digits of `S` and reading the result as a base-10 integer.

## Key observation
A permutation of `S` forms an `N`-digit string that may have leading zeros; we
interpret it as an integer (so leading zeros simply shrink the value). Two
permutations producing the same integer are counted once. Therefore the answer
is the number of distinct integers `v` such that:
1. `v` is a perfect square, and
2. `v`, when written with leading zeros padded to exactly `N` characters, is a
   permutation of `S` — equivalently, the multiset of digits of `v` (padded to
   length `N`) equals the multiset of digits of `S`.

The largest value representable is below `10^N`, so the largest candidate square
root is `floor(sqrt(10^N - 1))`. For N = 13 that is about 3.16 million roots,
which is cheap to enumerate.

## Algorithm
1. Read `N` and `S`. Compute the sorted digit multiset of `S` (a sorted tuple of
   its characters, or a Counter / length-10 count array).
2. Set `limit = 10**N` (exclusive upper bound on representable values).
3. For each integer `k` from 0 up to `floor(sqrt(limit - 1))`:
   - `sq = k*k`.
   - Format `sq` as a string zero-padded to width `N` (`str(sq).zfill(N)`).
     Since `sq < 10**N`, this string has exactly length `N`.
   - If the sorted characters of that padded string equal the sorted characters
     of `S`, count it.
4. Each distinct `k` yields a distinct `sq`, so distinct squares are counted
   automatically without a set.
5. Print the count.

## Edge cases
- Leading zeros: handled by zero-padding the square to width `N` before
  comparing multisets. E.g. for `S = "010"`, `1` pads to `"001"` and matches.
- `k = 0` (value 0) is included; `0` is a square and padding handles it.
- N = 1: trivially works; squares 0,1,4,9 compared to the single digit.
- No matches yields 0.

## Complexity
Roots up to ~3.16e6 for N = 13, each O(N log N) sort — well within limits.

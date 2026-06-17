# Count square numbers from permutations of digits of S

Verdict: logic-heavy — permutation enumeration with duplicate-value handling
and leading-zero subtlety. Planning first.

## Data & invariants
- N (1..13), S string of N digits.
- digit_count[0..9] = multiset of digits in S.
- A permutation maps to an integer in [0, 10^N - 1]. Different permutations may
  yield the same integer (e.g. swapping equal digits, or leading-zero forms).
- Output: count of DISTINCT square numbers reachable.
  Invariant: each square value counted at most once.

## Key insight
- N ≤ 13. Brute-forcing all N! permutations is too many (13! ≈ 6.2e9).
- Instead: iterate over all squares k^2 with k^2 < 10^N, and check whether
  k^2's digit multiset (padded to N digits, i.e. counting leading zeros) equals
  digit_count.
- Padding to N digits handles leading zeros correctly: e.g. value 1 with N=3 is
  "001", whose multiset {0,0,1} must match S's multiset. This naturally treats
  permutations that produce leading zeros (smaller-magnitude numbers).

## Control flow
```
read N, S
target[0..9] ← counts of each digit in S
limit ← 10^N           # values are 0 .. limit-1, so k from 0 .. floor(sqrt(limit-1))
answer ← 0
k ← 0
while k*k < limit:
    v ← k*k
    cnt[0..9] ← 0
    # decompose v into exactly N digits (pad with leading zeros)
    temp ← v
    for j in 1..N:
        cnt[temp mod 10] += 1
        temp ← temp // 10
    # temp must be 0 now since v < 10^N (guaranteed by loop bound)
    if cnt == target:
        answer += 1
    k ← k + 1
print answer
```

## Why no double counting
- We iterate over distinct values v = k^2, each once. A value is counted iff its
  N-digit (zero-padded) multiset equals S's multiset, meaning some permutation of
  S produces it. Distinct squares → distinct counts. Correct.

## Edge cases & failure modes
- N=1: values 0..9; squares 0,1,4,9 each single-digit; multiset match on the one digit.
- All zeros S (e.g. "000"): only v=0 matches (multiset all zeros); 0 = 0^2 is a
  square → counted once. k starts at 0 so v=0 included.
- Leading zeros: "010" → multiset {0,0,1}. v=1 → "001" matches; v=100 → "100"
  matches. Both counted → 2. Matches sample 2.
- 0 as a square: include k=0 (0 is a perfect square). Sample 2 counts value 1 and
  100, not 0 (since {0,0,1} ≠ {0,0,0}); fine.
- Large N=13: limit=10^13, k up to ~3.16e6 iterations, each O(13) → ~4e7 ops. OK.

## Interface contract
- Pure computation; reads stdin "N\nS", prints integer count to stdout.
- Uses big-enough integers (Python ints, no overflow concern).

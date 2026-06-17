# Plan: count distinct square numbers reachable by permuting digits of S

Verdict: logic-heavy — distinct-value dedup, leading-zero semantics, and
perfect-square test all have classic subtle bugs. Plan first.

## Data & invariants
- Input: N (1..13), S length-N digit string.
- A permutation maps to the integer formed by reading the permuted digits as
  a base-10 number. Leading zeros are NOT stripped: "010" permuted to digit
  order (0,1,0) is the integer 10; permuted to (1,0,0) is 100. The numeric
  value already collapses leading zeros automatically (int 010 == 10), so we
  do NOT special-case them — different digit orderings that yield the same
  integer must be counted once.
- KEY invariant: we count DISTINCT integer values that are perfect squares.
  Two permutations giving the same value count once (sample 2).
- N <= 13 so values fit in 64-bit (max < 10^13). Multiset of digits, not
  positions, determines reachable values.

## Approach
N up to 13 => 13! ~ 6.2e9 permutations: too many to enumerate naively, but
distinct digit multisets make many equal. Cleaner: iterate over candidate
square numbers and check if each can be formed from S's digit multiset.

- Range of values: from 0 up to (10^N - 1). The integer has AT MOST N digits.
  A formed value V uses exactly N digits as a string ONLY if no leading zero;
  but leading zeros vanish, so V's decimal representation has <= N digits and
  the "missing" high-order positions are zeros. So V is reachable iff:
  digit-multiset(V padded to length N with leading zeros) == digit-multiset(S).
  Equivalently: multiset of decimal digits of V, plus enough '0's to reach
  length N, equals multiset of S.

Flow:
  target_counts <- count of each digit 0..9 in S
  limit <- 10^N            # exclusive upper bound (max N-digit value + 1)
  answer <- 0
  k <- 0
  while k*k < limit:
    v <- k*k
    # build digit count of v as a number, then pad zeros to length N
    vc <- count of each digit in decimal string of v
    total_digits <- number of digits in v (1 if v==0)
    if total_digits <= N:
      vc[0] += N - total_digits        # pad high positions with zeros
      if vc == target_counts: answer += 1
    k += 1
  return answer

## Why this is correct & fast
- Each reachable integer V corresponds to exactly one square value; counting
  squares directly gives DISTINCT values automatically (no dedup needed).
- A square V is reachable iff its zero-padded N-length digit multiset matches
  S's multiset — exactly the permutation condition.
- Loop count ~ sqrt(10^13) ~ 3.16e6 iterations: fast.

## Edge cases
- N=1, S="0": squares < 10: 0,1,4,9. v=0 has digits {0:1} matches -> count.
  v=1 digits{1:1} != {0:1}. So answer 1 (just 0). Correct: 0 is 0^2.
- S all zeros: only V=0 matches (padded). 0 is a perfect square -> count 1.
- v=0: total_digits treated as 1, decimal string "0" gives vc[0]=1, then pad
  N-1 more zeros -> vc[0]=N. Matches S iff S all zeros. Correct.
- Leading-zero permutations: handled by padding, never double counted.
- N=13 max value 9999999999999, sqrt ~ 3162277; loop fine.

## Contract
- Read N then S from stdin. Print single integer count to stdout.

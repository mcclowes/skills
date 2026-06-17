# Count square numbers from permutations of digit string S

Verdict: logic-heavy — combinatorial counting with a duplicate-value trap and
a "leading zero" subtlety. Planning first.

## Data & invariants
- Input: N (1..13), S a string of N digit chars.
- Key insight: a permutation defines a multiset arrangement. Two permutations
  that produce the *same integer value* count ONCE. So we count distinct
  square VALUES achievable, not permutations.
- Digit count of S: cnt[0..9] = how many of each digit S contains.
  Invariant: sum(cnt) == N.
- A value V (0 <= V < 10^N) is achievable iff its decimal digit multiset,
  PADDED with leading zeros to exactly N digits, equals cnt.
  (Permuting can place zeros in front, e.g. "010" -> value 1 = "001" uses one 1,
   two 0s, matching cnt.)
  Invariant: the multiset of the N-length zero-padded representation of V == cnt.

## Control flow
Since N <= 13, value < 10^13. Iterate over candidate squares, not permutations.
  total_count <- 0
  max_val = 10^N   (exclusive upper bound; value has at most N digits)
  i <- 0
  while i*i < max_val:
      sq = i*i
      build digit-count of sq, padding to N digits:
        dcnt[0..9] = 0
        temp = sq
        for k in 1..N:                 # exactly N positions
            dcnt[temp % 10] += 1
            temp = temp // 10
        # after loop temp must be 0 (sq fits in N digits since sq < 10^N)
      if dcnt == cnt:  total_count += 1
      i += 1
  return total_count

Note: special case sq = 0 (i=0): padded N-digit rep is all zeros; matches only
if S is all zeros. Handled naturally by the loop starting at i=0.

## Edge cases & failure modes
- N = 1: values 0..9; squares 0,1,4,9. Count if single digit matches.
- S all zeros (e.g. "0000"): only value 0 (=0^2) matches -> answer 1.
- Leading-zero values: e.g. S="010", value 1 -> padded "001" multiset {0:2,1:1}
  == cnt of "010" -> counted. value 100 -> "100" multiset {0:2,1:1} also matches.
  Both are distinct square values (1 and 100) -> answer 2. Correct.
- Distinct-value dedup: iterating over each integer square value once means each
  achievable square counted exactly once automatically (no permutation double count).
- Upper bound: largest value < 10^13, so i up to ~3.16 million; loop is fast.
- temp leftover: since sq < 10^N, after N divisions temp == 0; no digits dropped.

## Interface contract
- Read N then S from stdin. Print single integer (count) to stdout.
- Pure computation; no mutation of input.

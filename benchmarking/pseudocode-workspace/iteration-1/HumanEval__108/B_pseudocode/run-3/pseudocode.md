# count_nums plan

Verdict: small but logic-sensitive — the "first signed digit is negative" rule for negative numbers is the trap. Planning the digit-sum just for that core.

Data: arr is list of ints (may be empty, may contain negatives, zero, positives).
Output: count of elements whose signed-digit-sum > 0.
  Invariant: digit sum of n and of -n differ only in the sign of the first (most significant) digit.

Signed digit sum of n:
  take s = abs(n), sum all its decimal digits normally
  if n < 0: the leading digit is counted negative instead of positive
    => signed_sum = normal_sum - 2 * (leading_digit_of_abs)
  positive / zero: signed_sum = normal_sum

Flow:
  count ← 0
  for each n in arr:
    if signed_digit_sum(n) > 0: count += 1
  return count

Edge cases:
  empty arr            → 0 (loop runs zero times)
  0                    → digit sum 0, not > 0, not counted
  positive single-digit→ digit equals value, > 0 counted
  -1                   → leading digit 1, signed = -1, not > 0, not counted
  11                   → 1+1=2 > 0 counted
  -11                  → 1+1=2, leading 1 → 2-2 = 0, not > 0, not counted
    (matches example: [-1,11,-11] → only 11 counts → 1)
  negative multi-digit like -123 → digits 1,2,3 normal=6, leading 1 → 6-2=4 >0 counted
    (-1+2+3 = 4, matches signed-digit definition)

Contract: pure; arr not mutated; returns int.

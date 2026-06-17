# count_nums

Mostly simple, but the "signed digit" rule is the one trap: for a negative number the
leading digit carries the sign, the rest are positive. e.g. -123 → -1 + 2 + 3 = 4.

## Data & contract
- Input: list of integers (may be empty, may contain 0, negatives, positives).
- Output: count of elements whose signed digit sum > 0.
- Pure; input not mutated.

## Signed digit sum of n
- Take absolute value, split into decimal digits.
- Sum all digits, but if n < 0, the first (most significant) digit is subtracted twice
  to flip its sign: sum_of_digits - 2*leading_digit.
  (equivalently: leading digit negative, rest positive)

## Control flow
- count ← 0
- for each n: if signed_digit_sum(n) > 0 → count += 1
- return count

## Edge cases
- empty list        → 0
- 0                 → digit sum 0, not > 0, excluded
- positive (1,11,2) → all sums positive, counted
- -1                → -1, excluded
- -11               → -1+1 = 0, excluded
- 11                → 1+1 = 2, counted
- single-digit neg (-5) → -5, excluded

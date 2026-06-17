# count_nums — plan

Verdict: small but has a subtle edge — signed digit sum for negatives. Plan the digit-sum core.

## Data & invariants
- Input: list of ints (may be empty, negative, zero).
- "Signed digit sum" of n: sum of decimal digits of |n|, but the first (most-significant) digit carries n's sign.
  - e.g. -123 → digits [1,2,3], first negated → [-1,2,3] → sum = 4.
  - 0 → digit sum 0.
- Output: count of elements whose signed digit sum > 0.

## Control flow
```
count ← 0
for each n in arr:
  s ← signed_digit_sum(n)
  if s > 0: count += 1
return count

signed_digit_sum(n):
  if n == 0: return 0
  sign ← +1 if n > 0 else -1
  m ← |n|
  digits ← decimal digits of m, most-significant first
  total ← sum of digits, with the FIRST digit multiplied by sign
  return total
```
Equivalent compact form: sum all digit values of |n|, then if n<0 subtract 2*(leading digit) to flip its sign.

## Edge cases
- empty input → loop runs 0 times → return 0.
- 0 → digit sum 0, not > 0, not counted.
- positive single-digit (e.g. 1) → sum = digit > 0 → counted.
- negative single-digit (e.g. -1) → only digit is leading, negated → -1 ≤ 0 → not counted.
- -11 → digits [1,1], leading negated → -1+1 = 0 → not counted.
- 11 → 1+1 = 2 > 0 → counted.
- multi-digit negative where tail outweighs leading (e.g. -123 → 4 > 0) → counted.

## Contract
- Pure; input not mutated; returns int ≥ 0.

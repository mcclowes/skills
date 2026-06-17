# Plan for count_nums

## Contract
`count_nums(arr)` takes a list of integers and returns an integer: the count of
elements whose signed digit sum is strictly greater than 0. The empty list
returns 0.

## Signed digit interpretation
For a negative number, the sign attaches to the leading digit only. For
example, -123 decomposes into the signed digits -1, 2, 3, summing to 4. So the
digit sum of a negative number equals (sum of digits of its absolute value)
minus twice the leading digit, or equivalently: take the absolute value, sum its
digits normally, then if the original was negative subtract 2 times the leading
digit. A cleaner formulation: convert the number to its decimal string, take the
first character group; if there is a minus sign, negate the first digit and add
the rest as positive digits.

## Algorithm
1. Define a helper `signed_digit_sum(n)`.
2. Convert `abs(n)` to a string, iterate its characters as integer digits.
3. If `n` is negative, negate the first digit before adding; remaining digits
   add positively.
4. In the main function, iterate `arr`, call the helper on each element, and
   count how many produce a sum strictly greater than 0.

## Edge cases
- Empty array -> 0.
- Zero: digit sum is 0, which is not > 0, so it does not count.
- Single-digit negatives like -5: signed sum is -5, not counted. -11 -> -1+1 = 0,
  not counted. This matches the example `count_nums([-1, 11, -11]) == 1` where
  only 11 (sum 2) counts.
- Positive numbers always have a positive digit sum unless the number is 0.

## Output
Return the accumulated count as an integer.

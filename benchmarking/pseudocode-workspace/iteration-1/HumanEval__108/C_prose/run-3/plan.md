# Plan: count_nums

## Input/output contract
`count_nums(arr)` takes a list of integers and returns an integer: the count of
elements whose "signed digit sum" is strictly greater than 0.

## The signed-digit rule
For a non-negative number, the digit sum is the ordinary sum of its decimal
digits. For a negative number, the leading (most significant) digit carries the
negative sign; all remaining digits stay positive. So `-123` decomposes into
signed digits `-1, 2, 3`, giving a sum of `4`. The number `-11` decomposes into
`-1, 1`, summing to `0`, which is not `> 0` and therefore is not counted.

## Algorithm
1. Initialise a counter to 0.
2. For each number `n` in `arr`:
   a. Take the absolute value and convert to a string to read its digits, or
      iterate digit by digit.
   b. Sum the digits of the absolute value.
   c. If `n` is negative, subtract twice the leading digit so that the most
      significant digit is treated as negative (equivalently, sum digits then
      flip the sign of the first digit).
   d. If the resulting signed sum is `> 0`, increment the counter.
3. Return the counter.

## Edge cases
- Empty list returns 0.
- `0` has digit sum 0, not counted.
- Negative single-digit numbers like `-5` give sum `-5`, not counted.
- Numbers where the negative leading digit cancels the rest (e.g. `-11` -> 0)
  are not counted.
- Large numbers and multi-digit positives work via straightforward digit summation.

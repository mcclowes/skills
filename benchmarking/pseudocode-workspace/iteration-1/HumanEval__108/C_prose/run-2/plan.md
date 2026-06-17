# Plan for count_nums

## Contract
- Input: `arr`, a list of integers (may be empty, may contain negatives, may contain zero).
- Output: an integer — the count of elements whose "signed digit sum" is strictly greater than 0.

## Definition of signed digit sum
For a non-negative number, the signed digit sum is just the ordinary sum of its decimal digits. For a negative number, the leading (most significant) digit contributes its negative value, while all remaining digits contribute their normal positive values. For example, `-123` decomposes into signed digits `-1, 2, 3`, giving a sum of `4`. `-11` decomposes into `-1, 1`, summing to `0` (so it does not count). `0` has digit sum `0`.

## Algorithm
1. Initialise a counter to 0.
2. For each number `n` in `arr`:
   a. Take the absolute value of `n` and convert it to its decimal digit string.
   b. Sum all of those digits as positive integers.
   c. If `n` is negative, the leading digit was counted as positive but should be negative, so subtract twice the leading digit value to correct it. Equivalently, compute the sum normally then, if negative, subtract `2 * (leading digit)`.
   d. If the resulting signed sum is strictly greater than 0, increment the counter.
3. Return the counter.

## Edge cases
- Empty array returns 0.
- Single-digit negatives like `-1` give sum `-1` (not counted).
- Zero gives sum 0 (not counted).
- Negatives whose trailing digits exactly offset the negative lead (e.g. `-11`, `-123`? no — `-123` is 4) are handled by the subtraction rule.

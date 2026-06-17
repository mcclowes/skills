# Plan for generate_integers

## Contract
- Input: two positive integers `a` and `b`. Their relative order is not guaranteed — `a` may be larger or smaller than `b`.
- Output: a list of integers representing the even single digits (2, 4, 6, 8) that fall within the inclusive range bounded by `a` and `b`, returned in ascending order.

## Interpretation
The phrase "even digits between a and b" refers to even *digits*, i.e. single-digit even numbers: 0, 2, 4, 6, 8. So the candidate set is constrained to the digits 0 through 9, and within that, only the even ones. The examples confirm this: `generate_integers(10, 14)` returns `[]` because no single digit lies in the range 10..14, and `generate_integers(2, 8)` returns `[2, 4, 6, 8]`.

## Algorithm
1. Normalise the bounds since order is not guaranteed: compute `low = min(a, b)` and `high = max(a, b)`.
2. Clamp the search to the single-digit range. The lower bound becomes `max(low, 0)` and the upper bound becomes `min(high, 9)` — only digits 0..9 can qualify.
3. Iterate over the clamped inclusive range and collect every value that is even (`n % 2 == 0`).
4. Because we iterate from low to high, the result is already in ascending order.

## Edge cases
- Reversed inputs (`a > b`): handled by min/max normalisation.
- Range entirely above 9 (e.g. 10..14): clamped upper bound < lower bound, loop produces empty list.
- `a == b`: range is a single value; included only if it is an even digit.
- Inclusive endpoints: both `a` and `b` are part of the range, matching the examples.

## Output
Return the collected list (possibly empty).

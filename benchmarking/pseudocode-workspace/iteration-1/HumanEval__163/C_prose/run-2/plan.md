# Plan for generate_integers(a, b)

## Input/output contract
The function takes two positive integers `a` and `b` (order not guaranteed) and
returns a list of integers. The result contains the even single-digit values
(0, 2, 4, 6, 8) that fall within the inclusive range bounded by `a` and `b`,
sorted in ascending order.

## Interpretation of the problem
Reading the examples carefully clarifies the intent. `generate_integers(2, 8)`
yields `[2, 4, 6, 8]` and `generate_integers(10, 14)` yields `[]`. This shows
the task is not about the even digits *of* the numbers, but about the even
single-digit integers (0, 2, 4, 6, 8) that lie inside the overlap of the range
`[a, b]` with the digit range `[0, 9]`. Because 10..14 contains no single-digit
values, the result is empty.

## Algorithm steps
1. Normalize the bounds: compute `low = min(a, b)` and `high = max(a, b)` so the
   function behaves identically regardless of argument order.
2. Clamp the effective range to single digits: `lower = max(low, 0)` (or 1 since
   inputs are positive) and `upper = min(high, 9)`.
3. Iterate over every integer `n` from `lower` to `upper` inclusive.
4. Keep `n` only if it is even (`n % 2 == 0`).
5. Collect the survivors into a list and return it (iteration order already gives
   ascending order).

## Edge cases
- Reversed arguments (`a > b`): handled by min/max normalization.
- Range entirely above 9 (e.g. 10..14): clamping makes `lower > upper`, so the
  loop produces an empty list.
- Equal bounds: a single value, included only if even and a single digit.
- Inputs are positive, so 0 will not appear in practice, but the logic remains
  correct if it did.

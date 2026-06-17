# Plan for make_a_pile

## Input/output contract
The function `make_a_pile(n)` accepts a single positive integer `n`. It returns
a list of `n` integers. The element at index `i` represents the number of stones
in level `i+1` of the pile. The returned list always has exactly `n` elements.

## The data
We are building a pile with `n` levels. The first level (index 0) always holds
exactly `n` stones. Each subsequent level holds two more stones than the level
beneath it. This is because the next number must keep the same parity as `n`:
if `n` is odd, the next odd number is `n+2`; if `n` is even, the next even
number is `n+2`. In both cases the step is +2, regardless of parity, so a single
uniform rule covers both branches described in the docstring.

## Algorithm steps
1. Generate the sequence starting at `n`, with each term increasing by 2.
2. Produce exactly `n` terms (one per level): `n`, `n+2`, `n+4`, ..., `n+2*(n-1)`.
3. Return these terms as a list, preserving order so index 0 is the bottom level.

The cleanest implementation is a list comprehension:
`[n + 2 * i for i in range(n)]`.

## Edge cases
- `n == 1`: the loop yields a single element `[1]`, which is correct since the
  pile has one level holding `n` stones.
- Parity: handled uniformly by the +2 step, so no separate odd/even branch is
  needed. For `n=3` we get `[3, 5, 7]`; for `n=4` we get `[4, 6, 8, 10]`.
- The problem guarantees a positive integer, so no validation for zero or
  negative inputs is required, though `range(n)` would naturally yield an empty
  list for non-positive `n`.

## Verification
`make_a_pile(3)` returns `[3, 5, 7]`, matching the documented example.

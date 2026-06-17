# Plan: make_a_pile

## Input/output contract
- Input: a positive integer `n`. It is the number of levels in the pile and also the count of stones in the very first level.
- Output: a list of `n` integers. The element at index `i` holds the number of stones in level `i+1`.

## Data involved
A single integer `n` drives everything. The result is a list built up across the `n` levels. No external data, no I/O, no mutation of inputs.

## Algorithm
The first level always has `n` stones. The key observation is the step pattern: each subsequent level adds 2 to the previous level's count. This is because:
- If `n` is odd, the "next odd number" after an odd value is `value + 2`.
- If `n` is even, the "next even number" after an even value is `value + 2`.

In both cases the parity of `n` is preserved through the whole pile and the increment is uniformly 2. So I do not actually need to branch on parity at all; the difference between consecutive levels is always 2.

Therefore the levels are simply `n, n+2, n+4, ..., n+2*(n-1)`. I will generate this with a list comprehension over `i` in `range(n)`, emitting `n + 2*i` for each.

## Edge cases
- `n == 1`: produces a single-element list `[1]`, which `range(1)` handles correctly.
- `n` is guaranteed positive per the spec, so no zero/negative handling is required, but the comprehension would simply return `[]` for `n <= 0`, degrading gracefully.

## Verification against example
`make_a_pile(3)` -> `[3, 3+2, 3+4]` = `[3, 5, 7]`, matching the docstring.

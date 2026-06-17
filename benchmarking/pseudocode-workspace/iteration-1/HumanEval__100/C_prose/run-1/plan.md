# Plan for make_a_pile

## Input/output contract
The function takes a single positive integer `n` and returns a list of `n`
integers. The element at index `i` represents the number of stones in level
`i + 1` of the pile. For the example `make_a_pile(3)` the result is
`[3, 5, 7]`.

## The data involved
We work with a single integer `n` and build a list of length `n`. Every value
in the list is itself an integer. The first element is always `n` exactly. Each
subsequent element grows from the one before it.

## The algorithm
The key observation is that the parity (odd/even) of `n` determines whether we
step to the next odd number or the next even number. Either way, the *next*
number of the same parity is simply the current value plus 2. So starting from
`n`, each successive level is the previous level plus 2. This holds regardless
of whether `n` is odd or even, because adding 2 preserves parity. Concretely:

- Level 1 has `n` stones.
- Level 2 has `n + 2` stones.
- Level `k` has `n + 2 * (k - 1)` stones.

I will produce the list with a comprehension that maps each index `i` in
`range(n)` to `n + 2 * i`. This is concise and avoids manual loop bookkeeping or
off-by-one errors.

## Edge cases
- `n = 1` returns `[1]`, a single level. The comprehension handles this
  naturally since `range(1)` yields only index 0.
- The problem guarantees `n` is a positive integer, so I do not need to handle
  zero, negatives, or non-integers.
- Both odd and even `n` are covered uniformly by the "+2 per level" rule, so no
  branching on parity is required, which keeps the code simple and correct.

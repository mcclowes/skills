# Plan for get_max_triples

## Input/output contract
- Input: a positive integer `n`.
- Output: an integer — the count of triples `(i, j, k)` with `1 <= i < j < k <= n`
  such that `a[i] + a[j] + a[k]` is divisible by 3, where `a[i] = i*i - i + 1`.

## Data
We conceptually build an array `a` of length `n` where each element is
`a[i] = i*i - i + 1` (using 1-based indices). We need to count unordered
index triples whose corresponding values sum to a multiple of 3.

## Key insight
Whether a sum is divisible by 3 depends only on each element's value modulo 3.
So instead of comparing actual values, compute `a[i] % 3` for each index and
count triples whose residues sum to `0 mod 3`. This avoids large-number issues
and clarifies the combinatorics.

## Algorithm
1. For each `i` from 1 to `n`, compute `a[i] = i*i - i + 1`, then its residue
   `r = a[i] % 3`. Tally counts of residues into buckets `c0`, `c1`, `c2`.
2. A triple sums to `0 mod 3` only when the three residues are:
   - all three `0`: choose 3 from `c0`.
   - all three `1`: choose 3 from `c1`.
   - all three `2`: choose 3 from `c2`.
   - one each of `0, 1, 2`: `c0 * c1 * c2`.
   (No other residue combination of three values sums to a multiple of 3.)
3. Sum these using the combination formula `C(m,3) = m*(m-1)*(m-2)/6`.

## Edge cases
- `n < 3`: no triple exists, every `C(m,3)` and the product term naturally
  yield 0, so the result is correctly 0.
- Large `n`: residue counting is O(n) and arithmetic stays small.

## Output
Return the total count as an integer.

# Plan for get_max_triples

## Input/output contract
- Input: a positive integer `n`.
- Output: an integer — the count of triples of indices `i < j < k` (with all
  indices in range `1..n`) such that `a[i] + a[j] + a[k]` is divisible by 3,
  where `a[i] = i*i - i + 1`.

## Data
The array `a` has length `n`, with `a[i] = i*i - i + 1` for `1 ≤ i ≤ n`.
Only divisibility by 3 matters, so what counts is each element's residue mod 3.

## Algorithm
The naive approach is three nested loops over all index triples, summing and
testing divisibility by 3 — that is O(n^3) and correct, but slow for large `n`.

A faster, equivalent approach: compute the residue `r = a[i] % 3` for each `i`
and bucket counts by residue (counts c0, c1, c2 for residues 0, 1, 2). A triple
of residues sums to a multiple of 3 only when the residues are:
- all three equal (0,0,0), (1,1,1), or (2,2,2), contributing C(count, 3) each;
- all three distinct (0,1,2), contributing c0 * c1 * c2.

So the answer is `C(c0,3) + C(c1,3) + C(c2,3) + c0*c1*c2`, where `C(m,3) =
m*(m-1)*(m-2)/6`. This is O(n).

## Edge cases
- `n < 3`: no valid triple exists; the formula naturally yields 0 because every
  combination term is 0.
- `n = 1` or `n = 2`: returns 0.
- Indices are 1-based per the spec; I iterate `i` from 1 to `n` inclusive.

I'll use the closed-form residue-counting approach for clarity and efficiency.

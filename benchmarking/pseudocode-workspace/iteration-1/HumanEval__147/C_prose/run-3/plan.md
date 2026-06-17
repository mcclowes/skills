# Plan for get_max_triples

## Contract
- Input: a positive integer `n` (the desired array length).
- Output: an integer — the count of index triples `(i, j, k)` with `i < j < k` such that `a[i] + a[j] + a[k]` is divisible by 3.

## Data
The array `a` has length `n`, with `a[i] = i*i - i + 1` for `i` running from 1 to `n` (1-indexed, matching the problem statement). For `n = 5` this yields `[1, 3, 7, 13, 21]`.

## Key insight
Whether a sum is a multiple of 3 depends only on each element's value modulo 3. So instead of tracking the actual values, I compute the residue `a[i] % 3` for every element. A triple's sum is divisible by 3 exactly when the three residues sum to a multiple of 3. The valid residue combinations are: all three equal to 0, all three equal to 1, all three equal to 2, or one of each (0, 1, 2).

## Algorithm
1. Build the residue list `r = [(i*i - i + 1) % 3 for i in range(1, n+1)]`.
2. Count occurrences of each residue: `c0`, `c1`, `c2`.
3. The answer is the number of ways to pick three from a single residue class plus the cross-class combinations:
   `C(c0,3) + C(c1,3) + C(c2,3) + c0*c1*c2`, where `C(m,3) = m*(m-1)*(m-2)/6`.

This is O(n) and avoids the naive O(n^3) triple loop.

## Edge cases
- `n < 3`: no triple exists, so all combination terms are zero and the result is 0 naturally.
- Combination terms with counts under 3 evaluate to 0 because of the falling-factorial form.
- `n = 1` or `n = 2`: returns 0.

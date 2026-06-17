# Plan

## Problem
Count triples (i, j, k) with i < j < k, A_i = A_k, and A_i != A_j.

## Input/output contract
- Input: line 1 is N; line 2 is N space-separated integers A_1..A_N.
- Output: a single integer, the count of valid triples.

## Approach
For a fixed middle index j, a valid triple needs a left endpoint i < j and a
right endpoint k > j with A_i = A_k = v for some value v != A_j. For each value
v, the number of (i, k) pairs straddling j with both equal to v is
left[v] * right[v], where left[v] = count of occurrences of v strictly before j
and right[v] = count strictly after j.

We want, for each j, the sum over all v != A_j of left[v]*right[v]. Iterating
over all v per j is too slow (O(N^2)). Instead, maintain a running total
S = sum over ALL v of left[v]*right[v] as j sweeps left to right, then subtract
the contribution of v = A_j (so the middle's own value is excluded).

Sweep: initialize left[v]=0 for all v, right[v] = total count of each value.
Process j from 1 to N. Before treating position j as a middle, we must move
element at j out of the "right" side: it is no longer to the right of j. So the
transition per index p:
1. Remove A_p from right (right[A_p] -= 1): updating S by removing old
   left*right term and adding new.
2. Now left/right reflect counts strictly left and strictly right of p.
   Add to answer: S - left[A_p]*right[A_p] (exclude same value as middle).
3. Add A_p to left (left[A_p] += 1): update S accordingly.

Maintaining S incrementally: whenever left[v] or right[v] changes, subtract the
old product term from S and add the new product term.

## Edge cases
- Values up to N: use arrays sized N+1.
- Large answer: Python ints are unbounded, no overflow concern.
- N up to 3e5: O(N) sweep with O(1) per step. Use fast input reading.

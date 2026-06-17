# Plan

## Problem
We have N distinct slime sizes. Size S_i has C_i slimes. We may repeatedly take two
slimes of the same size X and replace them with one slime of size 2X. We want to
minimize the total number of slimes remaining.

## Key insight
Each size behaves independently in terms of carry-propagation, but the carries flow
*upward* in a binary-like sense: if a size X has an even-ish count, pairs merge into
size 2X, which may itself already be a present size (or become a brand-new size).
Because sizes can only ever double (X -> 2X -> 4X ...), all sizes that can interact
share the same odd "base" (S divided out by its factor of 2). Within a chain
X, 2X, 4X, ..., counts behave like binary carrying: every pair at level k contributes
one slime at level k+1.

## Algorithm
Process sizes from smallest to largest. Maintain a dictionary mapping size -> current
count of slimes available at that size (including carried-in slimes from below).
Sort the sizes. Iterate in increasing order over a worklist that includes original
sizes plus any new sizes created by carrying. Use a sorted structure: put all initial
(S_i, C_i) into a heap/dict. Repeatedly pop the smallest size, take its count c:
- The number of pairs is c // 2, which carry up to size 2*size, adding c//2 to the
  count there (creating the entry if absent and pushing 2*size into the heap).
- The remainder c % 2 stays as leftover slimes that cannot be merged further at this
  size; add it to the answer.
Because doubling a size up to ~10^9 starting value with counts up to 10^9 only adds
O(log C) new levels per chain, total work is O((N + N log C) log) which is fine.

## Edge cases
- Single size, huge count (sample 3): repeated halving; answer = popcount-like result.
- Sizes already present as 2X: carries merge naturally via the dict.
- Counts of 1: contribute 1 directly.

## I/O contract
Read N, then N lines of "S C". Output a single integer: minimal slime count.

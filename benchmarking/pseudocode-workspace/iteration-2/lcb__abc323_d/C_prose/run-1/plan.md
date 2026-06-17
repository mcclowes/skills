# Plan

## Problem
We have slimes of various sizes; for size S_i there are C_i of them. Two slimes of
the same size X merge into one slime of size 2X. We want to minimize the total
number of slimes remaining.

## Key insight
Two slimes of size X become one of size 2X. So at any size X, if there are k
slimes, we can pair them up: floor(k/2) merges produce floor(k/2) slimes of size
2X, and k mod 2 (0 or 1) slime remains at size X. The merged slimes at 2X then
combine with any pre-existing slimes of size 2X, recursively. This is exactly
binary carry propagation, but only along chains of repeated doublings.

Because sizes can be up to 1e9 and counts up to 1e9, but N is at most 1e5, we
process sizes in increasing order using a dictionary (map) from size -> count.

## Algorithm
1. Read N pairs (S_i, C_i) into a dict `cnt[S] = C`.
2. Collect all distinct sizes and sort them ascending.
3. Maintain a count of leftover (irreducible) slimes = 0.
4. Iterate sizes in ascending order. For the current size X with count c:
   - leftover at this size = c mod 2 (these can never merge further at X).
   - add (c mod 2) to the answer.
   - carry = c // 2 slimes of size 2X.
   - if carry > 0: add carry to cnt[2X] (creating the entry if absent; if 2X is
     a new size, insert it so it gets processed later — but since we iterate a
     sorted list, we must handle newly created sizes). To handle this cleanly,
     process with a sorted structure where we can add 2X. Since 2X > X always,
     and we go in increasing order, adding to cnt[2X] and processing later works
     if we use a heap or re-sort. Simplest: use a heap of distinct sizes.

## Implementation detail (heap)
Push all initial sizes into a min-heap. Pop smallest size X, look up its current
count in the dict (skip if already consumed). Compute leftover and carry. If
carry creates/updates size 2X and 2X was not already pending in the heap, push
it. Use a `seen`/pending set to avoid duplicate heap entries, or just allow
duplicates and skip when the dict count is zero (set count to 0 after processing).

## Edge cases
- Single size, odd count: leftover 1 plus whatever the carry chain leaves.
- Count 1: contributes 1, no carry.
- Large counts (1e9): pure integer arithmetic, no overflow concerns in Python.
- 2X may collide with an existing distinct size: dict handles the merge.

## I/O contract
Input: first line N, then N lines "S C". Output: single integer, the minimum
number of slimes.

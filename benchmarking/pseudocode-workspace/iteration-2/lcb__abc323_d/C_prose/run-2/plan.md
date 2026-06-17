# Plan

## Problem
We have N distinct slime sizes; size S_i appears C_i times. We may repeatedly take two
slimes of equal size X and replace them with one slime of size 2X. Minimise the total
number of slimes remaining.

## Data
- A mapping from size -> count. Sizes up to 1e9, counts up to 1e9, N up to 1e5.
- We cannot enumerate every integer size; only sizes that actually appear (originally
  or as products of synthesis) matter.

## Algorithm
Synthesis at a size X turns 2 slimes into 1 of size 2X. Given `count` slimes of size X,
we can perform `count // 2` syntheses, leaving `count % 2` slimes of size X behind and
adding `count // 2` slimes of size 2X. The leftover (`count % 2`, i.e. 0 or 1) can never
be reduced further at this size, so it contributes directly to the answer.

Process sizes in increasing order. Maintain a dict `cnt` of size -> count. Use a sorted
structure / heap so that when synthesis at X creates slimes of size 2X, those are folded
into the (possibly already existing, possibly new) bucket for 2X before we process 2X.

Steps:
1. Read pairs into a dict cnt.
2. Push all sizes into a min-heap.
3. Pop smallest size X. Let c = cnt[X]. answer += c % 2 (the unmergeable remainder).
   carry = c // 2. If carry > 0, add carry to cnt[2X]; if 2X was not present, push it.
4. Repeat until heap empty.
5. Print answer.

Because we always process the smallest remaining size first, any new 2X bucket is created
before it is popped, so carries accumulate correctly (chained doublings work).

## Edge cases
- Single size with huge count: repeated halving terminates (sum of set bits across the
  cascade), e.g. 1e9 -> answer 13 (popcount-like behaviour of the cascade).
- Counts that are odd at every level leave a 1 behind each level.
- Sizes that collide only via doubling (e.g. 3 doubling to 6 which already exists).
- Guard against re-pushing a size already in the heap: track presence so each size is
  processed exactly once after all contributions to it are gathered.

## I/O contract
Input: first line N, then N lines "S_i C_i". Output: single integer, the minimum count.

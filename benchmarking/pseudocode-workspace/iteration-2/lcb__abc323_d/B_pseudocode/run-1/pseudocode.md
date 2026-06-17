# Slime synthesis — minimize final count

## Verdict
Logic-heavy: carry/binary accumulation over a map keyed by size, with merges
creating new sizes that didn't exist. Off-by-one risk in "how many remain at a
size" (C mod 2) and in propagating the carry. Planning first.

## Data & invariants
- count: map from size -> number of slimes currently at that size (size up to ~10^9 * 10^9 range, use dict).
- Process sizes in ascending order. New sizes (2X) are always larger than X, so
  ascending processing guarantees that when we reach a size, all merges that could
  have fed into it from smaller sizes have already been applied.
  Invariant: when we pop the smallest size X, count[X] is final (no smaller size
  can ever produce X, since merges only double — they go upward).
- answer accumulates the number of slimes that remain un-mergeable at each size.

## Control flow
- Read pairs (S_i, C_i) into count (sizes distinct per constraints).
- Use a min-heap (or sorted processing with a heap, because merges insert new sizes
  2X that may be larger than the current max and must be revisited in order).
- ans <- 0
- while heap not empty:
    X <- pop smallest size present in heap (skip stale entries: only process if
         X still in count and not already done)
    c <- count[X]
    pairs <- c // 2          # number of merges -> that many slimes of size 2X
    leftover <- c % 2        # 0 or 1 slime stays at size X forever
    ans <- ans + leftover
    if pairs > 0:
       Y <- 2 * X
       if Y not in count: push Y onto heap
       count[Y] <- count[Y] + pairs
    remove X from count (mark done)

  To avoid duplicate heap pushes, only push a size when it first becomes present
  with nonzero count. Simpler: push every newly-created size once; guard popping
  with a "processed" set so stale/duplicate pops are ignored.

## Edge cases
- Single size, C=1 -> pairs=0, leftover=1, ans=1.
- C=10^9 at one size (sample 3): repeatedly halving with carry. 10^9 in binary has
  13 set bits -> ans=13. The doubling chain X, 2X, 4X... each contributes its
  carried count's parity. Verified by binary popcount intuition.
- Two distinct sizes where one merges into the other's chain: e.g. size 3 (c=3) ->
  1 pair to size 6. Size 6 already had 1 -> becomes 2 -> 1 pair to 12, leftover 0.
  Size 3 leftover 1, size 5 leftover 1, size 12 leftover 1 => ans 3. (sample 1)
- Sizes that never collide: each contributes popcount(C_i) effectively => ans is
  sum, but collisions can reduce it.
- Large numbers: 2*X can exceed 10^9; Python big ints fine.

## Interface contract
- Input via stdin: N, then N lines "S C".
- Output: single integer = minimal final slime count.
- Pure computation; deterministic.

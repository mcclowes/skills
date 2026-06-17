# Slime synthesis — minimize slime count

## Verdict
Logic-heavy: a "binary carry" process over a sparse map of sizes, with carries
cascading into possibly-new sizes. Off-by-one / carry-propagation bugs likely.
Planning first.

## Data & invariants
- `counts`: map size -> count (count ≥ 1 for present sizes).
- Two slimes of size X (X present, count ≥ 2) merge into one of size 2X.
  So for a given size X with count c: we can form floor(c/2) slimes of 2X,
  leaving c mod 2 of size X. The floor(c/2) get *added* to size 2X's count.
- Invariant: total "answer" = sum over all sizes of (final count at that size),
  where each size's final count is c mod 2 AFTER all carries into it are applied.
- Key ordering invariant: process sizes in INCREASING order. When we process X,
  all merges from smaller sizes that could carry into X have already been
  applied, so counts[X] is final-before-its-own-merge. Carries from X go to 2X > X,
  processed later. This guarantees each size is finalized exactly once.

## Control flow
1. Read pairs (S_i, C_i) into map counts[S_i] = C_i.
2. Use a min-heap / sorted structure of sizes present. Since carries create new
   sizes (2X) that may not be present, use a heap seeded with initial sizes,
   and push 2X when a carry first creates/adds to it.
   Simpler: maintain a dict + a min-heap of distinct sizes; lazily handle.
3. answer ← 0
4. Pop sizes from heap in increasing order (skip stale/duplicate pops):
   - let c = counts[size]
   - pairs = c // 2 ; leftover = c % 2
   - answer += leftover
   - if pairs > 0:
       nb = 2 * size
       if nb not in counts: counts[nb] = 0; push nb to heap
       counts[nb] += pairs
   - (mark size processed)
5. Output answer.

### Heap staleness handling
- A size 2X may be pushed when first created. If 2X was already an initial size
  not yet processed, it's already in heap — avoid double processing.
- Track a `processed` set OR only push a size when newly created (counts key
  didn't exist). Initial sizes are all pushed once at start. So each distinct
  size is in the heap exactly once. When we pop it, counts[size] already
  includes all carries from smaller sizes (since those were processed earlier).
- Therefore: seed heap with all initial sizes; when a carry creates a brand-new
  size, push it. Never push an already-existing size again. Each size popped once.

## Edge cases & failure modes
- Single size, large count (e.g. 1e9): count // 2 chains many times. The chain
  length is ~log2(count) ≈ 30, and carry produces new sizes 2X,4X,... each with
  its own count. Sample 3: C=1e9 → answer 13 (popcount-like / repeated halving
  with leftovers). Must use big ints (Python native, fine).
- count = 1: leftover 1, no pairs, contributes 1.
- Carry into an existing-but-not-yet-processed initial size: counts[nb] += pairs
  before nb is popped; correct because nb > size so processed later. Do NOT
  re-push nb.
- All distinct sizes count 1 (sample 2): every size leftover 1, no merges → N.
- Overflow: sizes can grow to ~1e9 * 2^30, fine in Python.

## Why answer for 1e9 is 13
Process size s with count c: leftover c%2 stays; c//2 promoted to 2s.
This is exactly: write the multiset and repeatedly halve-with-remainder along a
single doubling chain (since only one initial size, all carries stay in chain
s, 2s, 4s, ...). The leftovers are the binary digits of c... but with the chain
continuing, total = popcount(c)?? 1e9 popcount = 13. Yes: single chain reduces
to popcount(C). Confirms answer 13.

## Interface contract
- Input: stdin, N then N lines "S C".
- Output: single integer (min slimes) to stdout.
- Pure computation, big ints, O((N + carries) log) where carries ≤ ~N*30.

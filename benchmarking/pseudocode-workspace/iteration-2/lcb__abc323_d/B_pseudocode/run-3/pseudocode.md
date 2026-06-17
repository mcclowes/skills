# Minimum slimes after synthesis

Verdict: invariant-heavy carry propagation across sizes — planning first.

## Data & invariants
- map: size -> count of slimes of that size (counts ≥ 1 initially, sizes distinct).
- Synthesis: 2 slimes of size X -> 1 slime of size 2X.
- For a fixed size X with count c: keep c%2 of them, the floor(c/2) pairs become
  floor(c/2) slimes of size 2X, which ADD to whatever already sits at 2X.
- Process sizes in INCREASING order so that carries into 2X are accounted for
  before we process size 2X. (2X > X always, since X ≥ 1, so 2X processed later.)
- Invariant: when we process size s, its count already includes all carries from
  smaller sizes that doubled into s.

## Control flow
```
read pairs (S_i, C_i) into map count[S] = C
answer ← 0
for each size s in ascending order of keys present in map:
    c ← count[s]
    leftover ← c mod 2          # slimes of size s that cannot pair
    carry ← c div 2             # pairs -> slimes of size 2s
    answer ← answer + leftover
    if carry > 0:
        count[2s] ← count.get(2s, 0) + carry   # may create new key 2s
return answer
```
- Iterating "ascending keys present" must include keys created during iteration
  (e.g. 2s newly added). Use a structure that lets us always pull the smallest
  unprocessed size next (e.g. process by repeatedly taking min, or a sorted
  iteration that re-checks). Simplest correct approach: maintain a sorted set /
  heap of sizes; pop smallest, process, push 2s if new.

## Edge cases & failure modes
- Single size, huge count (e.g. C=1e9): pure binary popcount-style reduction.
  1e9 in binary has 13 set bits → answer 13. Carries cascade up many doublings;
  values 2s can exceed 1e9·2^30 → use big ints (Python ints are unbounded, fine).
- No pairing possible (all counts = 1, no two sizes where one doubles into
  another) → answer = N.
- Carry into an existing size: must add, not overwrite; that combined count may
  itself pair again (handled because we process s before 2s).
- Chain: 3@size3 -> 1 left + 1 carry to 6; existing 1@6 + 1 = 2@6 -> 0 left +
  1 carry to 12. Final: size3=1, size5=1, size12=1 => 3. Matches sample 1.
- Duplicate creation of key 2s: guard against pushing same size to heap twice;
  only push when the key is newly created (count was absent). If it already
  exists and is unprocessed it'll be handled when popped. Safer: just add to
  count, and drive iteration purely by a heap of distinct sizes, marking
  processed sizes; or accumulate carries and only process each size once.

## Chosen concrete method (avoids double-processing)
Use a min-heap of distinct sizes plus the count map.
```
heap ← all initial sizes
while heap not empty:
    s ← pop smallest
    if s already processed: skip   # dedupe pushes
    mark processed
    c ← count[s]
    answer += c mod 2
    carry = c div 2
    if carry:
        if 2s not in count: push 2s to heap
        count[2s] = count.get(2s,0) + carry
```
Because s is the smallest unprocessed, and 2s > s, 2s is never processed before
its carry is applied. Each size popped once → O(K log K), K = distinct sizes
reachable (bounded; total work small).

## Interface contract
- Input via stdin: N, then N lines "S C".
- Output: single integer (minimum slime count) to stdout.
- Pure arithmetic; big integers required (Python handles natively).

# Plan: Keyence printer scheduling (ABC325 D)

Verdict: greedy + min-heap scheduling with a subtle tie/ordering invariant. Logic-heavy, plan first.

## Problem restated
- Product i is printable during the closed interval [L_i, R_i] where L_i = T_i, R_i = T_i + D_i.
- Printer prints at most one product at any chosen real time; after a print it needs 1 microsecond before the next print. So if we print at time t, next print must be at time ≥ t+1.
- KEY OBSERVATION: we only ever need to print at INTEGER times relative to a base, because each interval has integer endpoints and the +1 charge gap is integer. Process printing times as integers t = current_time, then t+1, t+2, ...
  Each window [L_i, R_i] contains integer t iff L_i ≤ t ≤ R_i (endpoints integer, so any integer in range works). We schedule one product per integer time slot, slot must satisfy L ≤ slot ≤ R.
- Maximize number of products assigned to distinct integer slots, each product placed at a slot within its window.

This is the classic "maximize jobs each with a release time L and deadline R, unit processing, machine does one unit time per job" => greedy: sort by L, use a min-heap of deadlines.

## Data & invariants
- products: list of (L, R).
- min-heap `pq` holds deadlines R of products currently "candidate" for the current time slot.
- current time `t` advances over the sorted distinct L values; at each L we add all products with that L into pq, then we assign as many slots as we can up to the next L.
- Invariant: pq contains only products with L ≤ current slot time and not yet assigned. We greedily assign the smallest deadline first (earliest-expiring) to each successive integer slot.

## Control flow (event-sweep greedy)
```
build products (L=T, R=T+D)
sort products by L ascending
pq <- empty min-heap (by R)
count <- 0
i <- 0  (index into sorted products)
t <- undefined (next free slot time)

while i < N or pq not empty:
    if pq empty:
        # jump time forward to next product's L
        t <- products[i].L
    # bring in all products whose L <= t
    while i < N and products[i].L <= t:
        push products[i].R into pq
        i <- i+1
    # try to assign current slot t to the candidate with smallest R
    R_min <- pop min from pq
    if R_min >= t:        # window still open at time t
        count <- count + 1
        t <- t + 1        # charge gap; next slot
    else:
        # this product's deadline already passed; discard it, do NOT advance t
        # (its window closed before t; it can't be printed)
        discard
    # loop continues
```

Refinement on time advancement: when pq nonempty we keep slot t; after a successful assign t becomes t+1. After discarding an expired item we retry same t. When pq becomes empty we must also be able to fast-forward t to the next L — handled at top of loop. But careful: after assigning we set t+1; if next product L is far ahead and pq still has items, we keep using t+1, t+2... which is correct (slots are free). If pq empties and i<N with products[i].L > t, top-of-loop sets t = products[i].L (jump forward, no wasted slots matter since we maximize count not minimize time).

## Edge cases
- N=1 → push one, assign, count=1.
- Multiple products same L and same R → heap handles; assign one per slot t, t+1, ... as long as ≤ R.
- Very large values up to 1e18 → use Python ints, no overflow.
- A product whose window is entirely behind current t (because earlier products consumed slots) → popped, R_min < t, discarded without advancing t. Correct: it cannot be printed.
- pq empty but products remain with large L → jump t forward.
- Touching/boundary: printing allowed at moment of entry or leave, so condition is R_min >= t (inclusive) and L <= t (inclusive). Use ≥ and ≤.

## Termination
- Each loop iteration either advances i (adding products) or pops one item from pq. Total pops ≤ N, total i increments ≤ N. So O(N log N) overall.

## Interface contract
- Read N then N lines of T D from stdin.
- Print single integer: max products printable.

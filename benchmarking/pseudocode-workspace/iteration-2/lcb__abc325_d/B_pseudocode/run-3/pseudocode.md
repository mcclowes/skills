# abc325_d — Printing Machine

## Verdict
Invariant-heavy greedy scheduling (interval-point matching with cooldown). Plan first.

## Problem restatement
Product i is in range during the closed interval [L_i, R_i] where L_i = T_i, R_i = T_i + D_i.
The printer prints at distinct times, each print on a product whose interval contains that time,
and consecutive prints must be >= 1 microsecond apart. Maximize number of products printed.

## Key insight
Because times can be real-valued and cooldown is exactly 1, scheduling reduces to integer slots:
we can always pick print times t, t+1, t+2, ... (integers). The classic equivalent problem:
- Sort all products by R_i (deadline) ascending — but standard efficient method sweeps by start.
- Greedy: process candidate print "time slots" in increasing order. At each integer time `cur`,
  among all products already available (L_i <= cur) and not yet expired (R_i >= cur), print on the
  one with the smallest R_i (earliest deadline). Advance cur by 1.

This is the "assign each unit-time job-with-deadline" greedy = maximize matched intervals where each
print consumes a unit slot. Min-heap keyed by R_i.

## Data & invariants
- products: list of (L, R) with L <= R.
- Sort products by L ascending.
- heap: min-heap of R values of products that are "active" (L <= cur) and not yet expired.
  Invariant: every R in heap satisfies R >= cur (we pop expired ones before printing).
- cur: the next integer time we will attempt to print at. Monotonically non-decreasing.
- printed: count of successful prints. Equals heap pops that succeed.

## Control flow
```
read N, products = [(T_i, T_i + D_i)]
sort products by L ascending
i ← 0                      # pointer into sorted products
heap ← empty min-heap (of R)
printed ← 0
cur ← undefined

while i < N OR heap not empty:
    if heap empty:
        # jump cur to the start of the next product
        cur ← products[i].L
    # add all products whose L <= cur into heap
    while i < N AND products[i].L <= cur:
        push products[i].R onto heap
        i ← i + 1
    # discard expired products (R < cur) — they can never be printed now
    while heap not empty AND heap.top < cur:
        pop heap
    if heap empty:
        continue        # nothing available at cur; loop will jump via products[i].L
    # print on earliest-deadline available product
    pop heap
    printed ← printed + 1
    cur ← cur + 1       # cooldown advances time by 1

print printed
```

## Why earliest-deadline (min R) is correct
Classic exchange argument: at time `cur`, among feasible products, choosing the one with the
smallest R never hurts — products with larger R remain feasible longer, so deferring them loses
nothing. Discarding products with R < cur is mandatory: they expired.

## Edge cases
- N = 1                     → one product, prints 1.
- Two products same L, same R, R == L: e.g. [1,2],[1,2]. cur=1 print one (R=2>=1), cur=2,
  print other (R=2>=2). printed=2. Correct (sample-like).
- Huge values up to 1e18 + 1e18 = 2e18 → Python big ints, no overflow concern.
- Product with R < cur after advancing: popped as expired, not counted. Correct.
- Gap between clusters of products: when heap empties, jump cur to next L (don't waste increments).
- Many products at same time but they expire same instant: each consumes one integer slot; if
  more products than the window can hold, extra ones expire and are skipped.

## Contract
Input: stdin N then N lines "T D". Output: single integer (max prints) to stdout.
Pure computation; reads all input first.
```
```
Sample checks:
  Sample1 -> 4
  Sample2 -> 2
  Sample3 -> 6
```

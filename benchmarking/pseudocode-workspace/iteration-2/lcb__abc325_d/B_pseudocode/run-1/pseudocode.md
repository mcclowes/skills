# Plan: max products printed (ABC325 D)

Verdict: logic-heavy greedy + heap with subtle time-advance invariant — plan first.

## Restatement
Product i is in range during closed interval [L_i, R_i] where L_i = T_i, R_i = T_i + D_i.
Printer prints one product per integer time t (we only ever need integer print times),
and after a print must wait 1 microsecond, so successive prints happen at strictly
increasing integer times t, t+1, t+2, ... (each print consumes one distinct integer slot,
and any two prints differ by ≥1). Maximize count of distinct products printed, each at
some time within its own [L_i, R_i].

Key reduction: this is the classic "schedule jobs each with a [release, deadline] window
on a single machine, each job takes 1 unit, max number completed." Optimal greedy:
process candidate times in increasing order; at each time pick (if any) the available
job with the EARLIEST deadline.

## Data & invariants
- products: list of (L, R), L ≤ R, integers up to 1e18.
- Sort products by L ascending (release time).
- heap: min-heap of deadlines R for products that are "released" (L ≤ current time t)
  and not yet printed.
  Invariant: every R in heap belongs to a product whose window already started by t.
- t: the next integer time at which we will attempt a print. Strictly increases by 1
  after each successful print.
- Invariant: each successful print uses a distinct integer time, times strictly increasing
  ⇒ the ≥1 charge gap is automatically satisfied.

## Control flow
sort products by L ascending
heap ← empty
i ← 0                      # pointer into sorted products
count ← 0
while i < N or heap not empty:
    if heap empty:
        # jump time forward to next release; no point sitting idle
        t ← L of products[i]
    # release all products with L ≤ t
    while i < N and products[i].L ≤ t:
        push products[i].R onto heap
        i += 1
    # discard products whose deadline already passed (R < t) — can't print them
    while heap not empty and heap.top < t:
        pop heap
    if heap not empty:
        pop heap            # print the earliest-deadline available product at time t
        count += 1
        t += 1              # charge: next possible print one microsecond later
    # if heap became empty here, loop will jump t to next release next iteration

print count

## Why earliest-deadline greedy is correct
At any decision time t, among products whose window covers t, printing the one with
smallest R is never worse: products with larger R remain printable later, the small-R
one is the most urgent. Standard exchange argument.

## Edge cases & failure modes
- N = 1 → print it (its window is non-empty since L ≤ R), answer 1.
- Two products both [1,2]: t=1 print one (R=2), t=2 the other still printable (R=2 ≥ 2). → 2.
  (matches sample 2 intuition / sample 1 touching cases.)
- Product with R = t exactly: still printable (closed interval, "<" used for discard so R=t kept).
- Huge values (1e18): use Python ints, no overflow concern.
- All windows identical and tiny relative to N: only as many as distinct integer slots inside
  [L, R] can be used; greedy + discard handles this (deadlines pop out as t passes R).
- Idle jump: when heap empties but products remain, set t to next L (don't waste iterations).

## Interface contract
Input via stdin: first line N, then N lines "T D". Compute L=T, R=T+D.
Output: single integer (max printable count) to stdout.
Pure computation; reads all input, prints one line.

## Complexity
Sort O(N log N), each product pushed/popped once → O(N log N). N ≤ 2e5, fine.

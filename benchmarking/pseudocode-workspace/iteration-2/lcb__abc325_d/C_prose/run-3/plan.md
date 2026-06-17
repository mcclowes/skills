# Plan

## Problem restated
Each product `i` is available to be printed during the closed interval `[T_i, T_i + D_i]`.
The printer prints at instantaneous moments. After printing it needs 1 microsecond before
printing again, so two prints must be at least 1 microsecond apart. We want the maximum
number of products printed, each at most once.

## Key insight
A classic observation: although time is continuous, an optimal schedule can be assumed to
print at integer microsecond times. If we sort events and always print at the earliest legal
integer time, that is optimal. The standard solution treats this as a greedy interval
scheduling with a "machine" that becomes free 1 unit after each print.

The well-known accepted approach: sort products by their right endpoint `R_i = T_i + D_i`
(deadline), and process them in that order. Maintain `current_time`, the earliest time the
printer is free. For each product (in deadline order), the earliest time we can print it is
`max(current_time, L_i)` where `L_i = T_i` is the left endpoint. If that time is `<= R_i`,
we print it there and set `current_time = printTime + 1`. Otherwise we skip it.

To break ties and handle many overlapping intervals correctly, a robust formulation uses a
min-heap: sweep over integer candidate times. Process events sorted by start; at each time
push all products that have started into a heap keyed by their deadline `R_i`; pop the one
with the smallest deadline that is still feasible (`R_i >= currentTime`), print it, advance
time by 1. Discard expired products (`R_i < currentTime`).

## Algorithm (heap sweep)
1. Read N products, store as `(L=T_i, R=T_i+D_i)`.
2. Sort by `L`.
3. Iterate using an index into the sorted list and a min-heap of deadlines `R`.
   Maintain `t` = current candidate print time.
   - Set `t` to the smallest start among remaining products if heap empty.
   - Push all products with `L <= t` into the heap.
   - Discard heap-top deadlines `< t`.
   - If heap nonempty, print (count++), pop, set `t += 1`.

## Edge cases
- Values up to 1e18: use Python ints (no overflow concern).
- Multiple identical intervals (sample 1: many `[1,2]`).
- N = 1.
- Far-apart intervals (sample 2): independent, both printable.

## I/O contract
- Input: first line N, then N lines of `T_i D_i`.
- Output: single integer, the max count.

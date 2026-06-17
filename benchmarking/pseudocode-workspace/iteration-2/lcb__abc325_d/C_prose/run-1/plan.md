# Plan: ABC325-D Keyence Printer

## Problem restated
Each product i is in the printer's range during the closed interval [T_i, T_i + D_i].
The printer prints instantly on one product at a time, but needs 1 microsecond of
charge between prints. So if it prints at time t, the next print can happen no earlier
than t + 1. We want the maximum number of products we can print on.

## Key observation
All interval endpoints are integers (T_i, D_i are integers). The optimal schedule can
always be shifted so that every print happens at an integer time. Reason: if a feasible
schedule exists, we can process products in order of their availability and assign each
to the earliest integer time >= its left endpoint that is still free and <= its right
endpoint. Two prints at distinct integer times automatically satisfy the 1-microsecond
charge gap, since consecutive integers differ by at least 1. So the constraint reduces
to: assign each chosen product a distinct integer time t with T_i <= t <= T_i + D_i.

## Algorithm (greedy with min-heap)
This is the classic "maximum matching of intervals to integer time slots" problem,
solvable greedily:
1. Compute each product's interval as left = T_i, right = T_i + D_i.
2. Sort products by left endpoint (ascending).
3. Sweep candidate integer time slots in increasing order. Maintain a min-heap of the
   right endpoints of all products whose left endpoint <= current time slot and which
   are not yet assigned.
4. At each slot we process: add all newly-available products (left <= current time) to
   the heap. Then, discard from the top of the heap any product whose right < current
   time (can never be printed now or later). If the heap is non-empty, assign the
   product with the smallest right endpoint to this slot (earliest-deadline-first),
   pop it, increment the answer, and advance to the next slot.

To avoid iterating over 10^18 time values, only advance the current time to meaningful
points: either the next product's left endpoint, or current time + 1 when we make an
assignment. Use index-driven sweep over sorted lefts.

## Edge cases
- N = 1: answer is 1 (always printable).
- Huge values up to 10^18: Python big ints handle this natively.
- Many products sharing the same interval: heap + slot advancement spreads them across
  consecutive integer slots, bounded by their common right endpoint.

## I/O contract
- Input: line 1 = N; next N lines = T_i D_i.
- Output: single integer, the max count, followed by newline.

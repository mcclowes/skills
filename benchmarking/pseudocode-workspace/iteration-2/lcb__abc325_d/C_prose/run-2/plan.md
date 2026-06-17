# Plan: Maximum products printed (ABC325-D)

## Data
Each product i has an availability interval `[L_i, R_i]` where `L_i = T_i` (when it
enters the printer range) and `R_i = T_i + D_i` (when it leaves). The printer can
print on at most one product at any integer? — actually any real instant, but a
print "uses" that product's interval, and consecutive prints must be at least 1
microsecond apart (charge time). We want to maximize the number of products printed.

## Reframing
Scale time so that each print occupies a 1-microsecond slot: if we print on product
i at time x, the next print must be at time >= x + 1. Because all interval endpoints
are integers and the gap constraint is exactly 1, an optimal schedule can always use
times drawn so that we pick the *earliest feasible* slot per product. This is the
classic problem solved by a greedy + min-heap:

- Sort products by their left endpoint `L_i` (entry time).
- Sweep a "current time" `cur`. Process products in order of `L`. Maintain a min-heap
  keyed by `R_i` (deadline = leave time) of products currently available
  (i.e., `L_i <= cur`).
- At each step, advance `cur` to the next candidate time. The standard approach:
  iterate candidate print times; at time `t`, among all products with `L_i <= t`
  and `R_i >= t` not yet used, choose the one with smallest `R_i` (most urgent),
  print it, then `cur = t + 1`.

## Algorithm (event-driven greedy)
Sort by L. Use index pointer + min-heap of deadlines.
Set `cur` to the smallest L. Loop:
1. Push all products with `L_i <= cur` into heap (key R_i).
2. Pop expired items with `R_i < cur`.
3. If heap nonempty: pop the smallest R (print it), count++, `cur += 1`.
4. Else: jump `cur` to the next product's L (no work to do meanwhile).
Stop when heap empty and no products remain.

## Edge cases
- Large values up to 1e18: Python big ints handle natively.
- Multiple products entering simultaneously.
- A product with R == cur is still printable (inclusive).

## I/O contract
Input: N, then N lines `T_i D_i`. Output: single integer = max prints.
Read fast via sys.stdin. Sample answers: 4, 2, 6.

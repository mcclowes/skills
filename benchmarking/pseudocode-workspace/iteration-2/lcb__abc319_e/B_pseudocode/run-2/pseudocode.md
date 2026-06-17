# Plan: earliest arrival at Aoki's house

## Key insight
P_i ∈ [1,8], so LCM(1..8) = 840. The transit time from bus stop 1 to bus stop N
(walking-from-house and walking-to-house excluded) depends ONLY on the arrival
time t at bus stop 1, modulo 840. Because every bus departs at multiples of P_i,
and all P_i divide 840, shifting arrival time at stop 1 by 840 shifts every
departure/arrival exactly by 840 (the wait pattern repeats with period 840).

So:
  answer(q) = q + X + f(  (q + X) mod 840  ) + ( ((q+X) - (q+X) mod 840) ... )
Cleaner: let A = q + X = arrival at stop 1.
  Let r = A mod 840, base = A - r.
  f(r) = arrival-time-at-stop-N when you arrive at stop 1 at time r.
  Then arrival at stop N when arriving at stop 1 at time A = base + f(r),
  because the whole bus pipeline is periodic with period 840.
  Final answer = base + f(r) + Y.

## Precompute f(r) for r in 0..839
For each starting residue r (treated as actual arrival time at stop 1):
  t = r
  for i = 1 .. N-1:
    # wait for next bus at stop i: depart at smallest multiple of P_i >= t
    dep = ceil(t / P_i) * P_i      # if t multiple of P_i, dep = t
    t = dep + T_i                  # arrive at stop i+1
  f[r] = t   # arrival time at stop N

This is O(840 * N) = 840 * 1e5 = 8.4e7 — acceptable.

## Data & invariants
- P: list length N-1, each in [1,8]. T: list length N-1, each >= 1.
- f: array length 840. Invariant: f[r] >= r (time only moves forward), and
  f[r] is the stop-N arrival time given stop-1 arrival exactly at r.
- Periodicity invariant: for any actual arrival A at stop 1,
  stopN_arrival(A) = (A - A mod 840) + f[A mod 840].
  Proof basis: adding 840 to t before the ceil step adds 840 to dep
  (since P_i | 840) and thus 840 to every subsequent t.

## Control flow per query
  A = q + X
  r = A mod 840
  ans = (A - r) + f[r] + Y
  output ans

## Edge cases
- N == 2: only one bus segment (i=1). Loop runs once. Fine.
  Wait — N=2 means stops 1 and 2, N-1 = 1 segment. Correct.
- Actually if N==2, there's 1 bus line. If the problem had N where N-1=0? No: N>=2 so >=1 segment. Fine.
- q = 0 → A = X, handled normally.
- Large values: q,X,Y,T up to 1e9, N up to 1e5. Max t ~ 1e9 + 1e5*1e9 ~ 1e14,
  plus base up to ~1e9. Use Python big ints (no overflow concern).
- ceil multiple: dep = ((t + P_i - 1) // P_i) * P_i. When t % P_i == 0 gives t. Correct
  (can board a bus if arriving exactly at departure).

## Interface contract
- Read N, X, Y; then N-1 lines of P_i T_i; then Q; then Q query lines.
- Output Q lines, the answer per query.
- Pure arithmetic; use sys.stdin for speed, build output list, join.

# abc319_e — earliest arrival at Aoki's house

Verdict: logic-heavy (ceiling-to-multiple timing + LCM precompute). Planning the core.

## Data & invariants
- N stops, X walk-to-stop-1, Y walk-from-stop-N.
- For i in 0..N-2: (P_i, T_i). 1 ≤ P_i ≤ 8.
- Key fact: any P_i divides L = lcm(1..8) = 840. So the *offset within a 840-window*
  fully determines the travel time through all buses. The added travel time is
  periodic in the start time with period 840.
- Precompute `add[r]` for r in 0..839 = total time spent (waiting + riding) traversing
  all N-1 bus segments, given arrival-at-stop-1 time ≡ r (mod 840).
  Invariant: add[r] is independent of the absolute time, only the residue matters,
  because each wait `ceil(t/P)*P - t` depends only on t mod P, and P | 840.

## Bus departure timing (the subtle bit)
At stop i, arrive at time t. Bus departs at multiples of P_i. Earliest departure ≥ t
is `ceil(t / P_i) * P_i`. Then arrive at next stop at that departure + T_i.
  If t is already a multiple of P_i → depart at t (catch it, no wait).
  ceil(t/P)*P = ((t + P - 1) // P) * P.

## Control flow
Precompute:
  L = 840
  for r in 0..L-1:
    t = r
    for i in 0..N-2:
      t = ceil(t / P_i) * P_i + T_i      # wait then ride
    add[r] = t - r                       # delta from arrival-at-stop-1 to arrival-at-stop-N

Per query q:
  t1 = q + X                             # arrive stop 1
  tN = t1 + add[t1 mod L]                # arrive stop N
  answer = tN + Y                        # walk to Aoki

Edge case N == 2: no buses, add[r] = 0 for all r → answer = q + X + Y. Loop range
0..N-2 is empty when N==2, so add stays 0. Correct.

## Edge cases & failure modes
- N == 2: no bus segments → just X + Y added. Handled (empty loop).
- t1 already a multiple of P_i: ceil gives t1 itself, zero wait. Handled by ceil formula.
- Large values (q,X,Y,T up to 1e9, N up to 1e5): tN up to ~1e9 + 1e5*2e9 ≈ 2e14, fits in
  64-bit / Python int.
- Q up to 2e5: each query O(1) after O(840 * N) precompute (~8.4e7 ops, fine).

## Interface contract
- Read N X Y, then N-1 lines P_i T_i, then Q, then Q lines q_i.
- Output Q lines, each the earliest arrival time.
- Pure arithmetic; no failure paths beyond input parsing.

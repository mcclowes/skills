# Count triples (i,j,k), i<j<k, A_i=A_k, A_i≠A_j

Verdict: counting problem with an inclusion/exclusion trick and per-value
prefix/suffix bookkeeping — easy to double-count or get the "≠" wrong.
Planning the core.

## Data & invariants
- A: 1-indexed sequence, length N, values in [1..N].
- For a fixed middle index j, a valid triple uses some value v = A_i = A_k with
  v ≠ A_j, where one occurrence of v is strictly left of j and one strictly right of j.
- For value v, let L_v = count of occurrences of v at positions < j (prefix),
  R_v = count at positions > j (suffix).
- Number of (i,k) pairs through j using value v = L_v * R_v.
- Invariant: at the moment we process index j, L is the multiset of counts strictly
  before j and R strictly after j (j's own value counted in neither).

## Key reduction
Sum over all middle j of (pairs with A_i=A_k=v through j, over ALL v)
minus the contribution where v = A_j (those violate A_i≠A_j).

For a fixed j:
  total_pairs(j) = sum over v of L_v * R_v
  bad_pairs(j)   = L_{A_j} * R_{A_j}     (these have A_i = A_j, disallowed)
  valid(j)       = total_pairs(j) - bad_pairs(j)

Computing sum_v L_v*R_v naively per j is too slow (N^2). Maintain it incrementally.

Let S = sum_v L_v * R_v, maintained as we sweep j left to right.
Initially (before any j) treat j conceptually moving from 1..N. We need, while at j:
  L = counts in [1..j-1], R = counts in [j+1..N].

Sweep approach:
- Precompute R_v = total count of v over the whole array initially as "everything
  to the right" — but j's own element must be removed before/while at j.
- Maintain S = Σ L_v R_v incrementally.

Detailed sweep (j from 1 to N):
  state before step: L holds counts of [1..j-1], R holds counts of [j..N]
    (i.e. j and everything after). S = Σ L_v R_v consistent with these.
  At index j with value a=A_j:
    1. Remove a from R (it should not be on either side):
         S -= L_a * R_a ; R_a -= 1 ; S += L_a * R_a
       Now L=[1..j-1], R=[j+1..N]. Correct sides for middle j.
    2. valid(j) = (S) - L_a * R_a        # subtract v=a contribution (bad)
       answer += valid(j)
    3. Add a to L (prepare for next j):
         S -= L_a * R_a ; L_a += 1 ; S += L_a * R_a
       Now L=[1..j], R=[j+1..N], matching the precondition for j+1.

Initialization: L all zero. R_v = total occurrences of v in whole array.
Then S = Σ L_v R_v = 0 (L all zero). Good.

Each update touches only value a, O(1). Total O(N). S fits in normal big ints
(Python handles arbitrary precision; max ~ N^2/4 ~ 2.25e10, fine).

## Edge cases
- N=3 minimum: works, loop over 3 middles.
- All distinct (sample 2): every L_v*R_v product is 0 or the only-pair has A_i=A_j
  filtered → answer 0.
- A_j value not appearing elsewhere: L_a*R_a = 0, no harm.
- Value appearing many times: counts accumulate correctly; product uses 64-bit-ish
  magnitudes (Python int safe).
- j=1: L empty so S=0, contributes 0. j=N: R becomes empty after removing self → 0.

## Interface contract
Read N then N ints from stdin. Print single integer (the count) to stdout.
Pure counting, no mutation of input semantics. answer is non-negative.

## Manual check sample 1: A = [1,2,1,3,2] (1-indexed)
Expected 3. Trust sweep; verify by running.

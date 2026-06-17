# get_max_triples — plan

Verdict: logic-heavy (modular counting + combinatorics). Plan first.

## Data & invariants
- a[i] = i*i - i + 1 for i in 1..n.
- Only each value's residue mod 3 matters for "sum is multiple of 3".
- Observe a[i] mod 3 = (i*i - i + 1) mod 3 = (i(i-1) + 1) mod 3.
  i(i-1) is product of consecutive ints → always even, and mod 3 cycles with i mod 3:
    i≡0: 0*2+1 = 1 → residue 1
    i≡1: 1*0+1 = 1 → residue 1
    i≡2: 2*1+1 = 3≡0 → residue 0
  So residue is 0 when i≡2 (mod 3), else 1.
- Count of residue-0 elements = c0, residue-1 elements = c1, residue-2 elements = c2 (c2 = 0 here).
  Invariant: c0 + c1 + c2 = n.

## Control flow
- A triple sums to 0 mod 3 iff the multiset of three residues sums to 0 mod 3.
  Valid residue-combos: (0,0,0), (1,1,1), (2,2,2), (0,1,2).
- Count triples:
  - choose 3 from c0: C(c0,3)
  - choose 3 from c1: C(c1,3)
  - choose 3 from c2: C(c2,3)
  - one from each: c0*c1*c2
- Since order i<j<k is just "choose a subset" (each unordered subset corresponds to exactly one ordered i<j<k), combination counts are correct.
- Simpler/robust alternative given small n: build residue counts by looping i=1..n, then apply formula. (Avoids any off-by-one in the analytic residue derivation; verify against it.)

## Edge cases
- n < 3 → no triples possible → all C(.,3) terms are 0 and product term: need all three counts ≥1. Returns 0 correctly.
- n = 5: residues for i=1..5 → [1,0,1,0,1] → c0=2, c1=3, c2=0.
  C(3,3)=1, C(2,3)=0, product=0 → total 1. Matches expected output 1.
- C(m,3) = 0 when m<3 (define helper to return 0).

## Interface contract
- Input: positive int n. Output: non-negative int count. Pure, no mutation.

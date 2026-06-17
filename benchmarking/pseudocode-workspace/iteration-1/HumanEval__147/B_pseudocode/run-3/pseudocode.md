# get_max_triples — plan

Verdict: number-theoretic counting. The naive O(n^3) is correct but the residue insight
is where a bug could hide. Plan first (short).

## Data & invariants
- a[i] = i*i - i + 1 for i in 1..n.  a[i] mod 3 only depends on i mod 3:
  - i ≡ 0: 0-0+1 = 1 mod 3
  - i ≡ 1: 1-1+1 = 1 mod 3
  - i ≡ 2: 4-2+1 = 3 ≡ 0 mod 3
  So residue is 0 when i ≡ 2 (mod 3), else 1.
- We count unordered index triples i<j<k whose a-values sum ≡ 0 mod 3.
- Sum of three residues ≡ 0 mod 3 happens iff: all three are 0, OR all three are 1
  (0+0+0=0; 1+1+1=3≡0). Mixed (two of one, one of other) gives 1 or 2, never 0.

## Control flow
- c0 = count of i in 1..n with i ≡ 2 (mod 3)   → residue 0
- c1 = n - c0                                    → residue 1
- answer = C(c0,3) + C(c1,3)   where C(m,3)=m*(m-1)*(m-2)/6, 0 if m<3

(O(1). A correct O(n^3) brute force would also work but is unnecessary.)

## Edge cases
- n < 3 → both binomials 0 → return 0.
- n=5: indices 1..5, i≡2 at i=2,5 → c0=2, c1=3. C(2,3)=0, C(3,3)=1 → 1. Matches example.

## Contract
- Input: positive int n. Output: int count. Pure, no mutation.

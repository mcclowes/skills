# get_max_triples — plan

Verdict: number-theoretic counting. The naive O(n^3) triple loop is correct but the
real logic is "count triples whose sum ≡ 0 mod 3" via residue classes. Plan that core.

## Data & invariants
- a[i] = i*i - i + 1 for i in 1..n. We only need a[i] mod 3, not a[i] itself.
- Group indices into residue counts c0, c1, c2 where ck = #{i : a[i] mod 3 == k}.
  Invariant: c0 + c1 + c2 == n.
- Order (i<j<k) is irrelevant to the *count* because each unordered set of 3 distinct
  indices is counted once via combinations — we count by residue multiset, not position.

## Residue of a[i]
- i*i - i + 1 = i(i-1) + 1. i(i-1) is product of consecutive ints → always even, but we
  need mod 3. Just compute (i*i - i + 1) % 3 per i. (Pattern repeats every 3, but explicit
  per-i compute is clear and cheap enough; n small.)

## Control flow
```
c = [0,0,0]
for i from 1 to n:
    r = (i*i - i + 1) mod 3
    c[r] += 1

count triples summing to 0 mod 3 from residues:
  (0,0,0): choose 3 from c0                      → C(c0,3)
  (1,1,1): choose 3 from c1                      → C(c1,3)
  (2,2,2): choose 3 from c2                      → C(c2,3)
  (0,1,2): one from each                          → c0*c1*c2
  (no other multiset of residues sums to 0 mod 3)
result = C(c0,3)+C(c1,3)+C(c2,3) + c0*c1*c2
```
- C(m,3) = m*(m-1)*(m-2)//6, and = 0 for m<3 (formula yields 0 naturally for m=0,1,2).

## Why those are the only multisets
Residue triples (unordered) summing to 0 mod 3: {0,0,0},{1,1,1},{2,2,2},{0,1,2}.
Check: {1,1,1}=3≡0, {2,2,2}=6≡0, {0,1,2}=3≡0. Others like {0,0,1}=1 no, {1,1,2}=4≡1 no, etc.

## Edge cases
- n < 3 → no triples possible → all C(.,3)=0 and at least one of c0/c1/c2 small → result 0. Handled by formula.
- n == 5 example: a%3 = [1,0,1,1,0] → c0=2,c1=3,c2=0.
  C(2,3)=0, C(3,3)=1, C(0,3)=0, product=0 → 1. Matches expected output.

## Contract
- Input: positive int n. Output: non-negative int count. Pure, no mutation of external state.

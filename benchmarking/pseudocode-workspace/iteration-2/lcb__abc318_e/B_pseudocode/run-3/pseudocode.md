# Plan: count triples (i<j<k) with A_i=A_k, A_i!=A_j

Verdict: logic-heavy counting with a closed-form risk of off-by-one. Plan first.

## Data & invariants
- positions[v] = sorted list of 1-based indices where A equals v (built in order, so already ascending).
- For a value v with positions p_1<...<p_m:
  - For a pair (p_a, p_b), a<b: indices strictly between = p_b - p_a - 1.
    Of those, count equal to v = (b - a - 1) (the positions p_{a+1}..p_{b-1}).
    Valid j (A_j != v) = (p_b - p_a - 1) - (b - a - 1) = (p_b - p_a) - (b - a).
  - Invariant: valid j count is >= 0 (since between consecutive same values, position gap >= index gap).

## Control flow
1. Read N and array A.
2. Build positions[v] for each value (append index as we scan; 1-based or 0-based both fine as long as consistent — use 0-based array index, differences are unaffected).
3. answer = 0
4. For each value v with list P of length m:
     contribution = sum over a<b of (P[b] - P[a]) - (b - a)
     - Term1 = sum over a<b of (P[b]-P[a]):
         using prefix: for b from 0..m-1, P[b]*b - (prefix sum of P[0..b-1]).
     - Term2 = sum over a<b of (b - a):
         for b, sum_{a<b}(b-a) = sum_{d=1..b} d = b*(b+1)/2... careful: a ranges 0..b-1, b-a ranges 1..b => sum = b*(b+1)/2.
         Actually b-a for a in 0..b-1 gives values b, b-1, ..., 1 => sum = b*(b+1)/2.
     contribution = Term1 - Term2 (accumulate as we go).
5. Print answer.

## Edge cases
- value appears < 2 times → no pairs → contributes 0 (loop handles naturally).
- N=3 minimal → handled.
- All distinct → answer 0 (sample 2).
- Large N=3e5 → O(N) total, use 64-bit (Python ints fine).

## Interface contract
- Input from stdin: first line N, second line N integers.
- Output: single integer (the count) to stdout.

## Verification against samples
- Sample1: 1 2 1 3 2 -> expect 3.
- Sample3: expect 20.

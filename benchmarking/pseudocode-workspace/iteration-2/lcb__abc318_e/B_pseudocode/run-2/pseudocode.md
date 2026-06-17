# Count triples (i<j<k), A_i = A_k, A_i != A_j

Verdict: combinatorial counting with an inclusion subtraction — easy to double-count
or mis-handle the "middle equals endpoints" case. Plan first.

## Data & invariants
- A: 1-indexed sequence length N, values in [1,N].
- For each value v, let positions p_1 < p_2 < ... < p_m be the indices where A = v.
- A "frame" is a pair (i,k) with A_i = A_k = v and i < k.
- The j must satisfy i < j < k. Total interior slots = k - i - 1.
- Of those interior slots, some hold value v (must be excluded, since A_j must != v=A_i).
- Answer = sum over all frames of (interior_count - interior_count_equal_to_v).

Invariant: every valid triple counted exactly once, keyed by its (i,k) endpoint pair.
Since A_i must equal A_k, grouping by value and by endpoint pair is a partition of all
valid triples — no overlap.

## Reformulation to avoid O(N^2) frames
For a fixed value v with positions p_1..p_m:
- term1 = sum over all pairs (a<b) of (p_b - p_a - 1)   [all interior slots]
- term2 = sum over all pairs (a<b) of (count of v-positions strictly between p_a and p_b)
- contribution = term1 - term2

term2 closed form: a v-position p_c (with index c, 1-based among the m) lies strictly
between p_a and p_b iff a < c < b. Number of (a,b) pairs enclosing it = (c-1)*(m-c).
So term2 = sum over c of (c-1)*(m-c).

term1: sum over pairs of (p_b - p_a) minus number of pairs.
  sum over pairs (a<b) of (p_b - p_a)
    = sum_b p_b*(b-1) - sum_a p_a*(m-a)   [each p_idx weighted by #pairs where it's larger minus #where smaller]
    equivalently iterate: prefix = running sum of p_a for a<b; add p_b*(b-1) - prefix.
  number of pairs = m*(m-1)/2.
  term1 = (sum over pairs of p_b - p_a) - m*(m-1)/2.

## Control flow
read N, A
group indices (0-based ok, use position values consistently) by value
ans <- 0
for each value v with position list P (sorted ascending, length m):
    if m < 2: continue
    # term1
    prefix <- 0
    pairgap <- 0
    for b from 0 to m-1:
        pairgap += P[b]*b - prefix     # P[b] minus each earlier P[a], summed
        prefix += P[b]
    numpairs <- m*(m-1)/2
    term1 <- pairgap - numpairs
    # term2
    term2 <- 0
    for c from 0 to m-1 (1-based cc = c+1):
        term2 += (cc-1)*(m-cc)
    ans += term1 - term2
print ans

Note positions can be 0- or 1-based; gaps (p_b - p_a) are translation-invariant, so
either is fine as long as consistent.

## Edge cases
- value appears < 2 times -> no frame -> skip.
- all distinct -> every m=1 -> ans 0 (sample 2).
- adjacent equal pair p_a, p_{a+1} with k-i-1 = gap-1 interior, possibly 0 interior -> term1 handles via gap.
- many repeats of same value (e.g. four 11s) -> term2 subtracts the interior same-value j's correctly.
- N up to 3e5; values up to N; everything O(N) total. Use Python big ints (no overflow concern).

## Contract
- stdin: line1 N, line2 N integers.
- stdout: single integer (the count). Always non-negative.

## Verify sample 1: A = 1 2 1 3 2 (0-based positions)
v=1: P=[0,2], m=2. pairgap: b=0 ->0; b=1 -> 2*1-0=2 => 2. numpairs=1. term1=1. term2: c=0:(0)*(1)=0; c=1:(1)*(0)=0 =>0. contrib=1.
v=2: P=[1,4], m=2. pairgap=4-1=3. numpairs=1. term1=2. term2=0. contrib=2.
v=3: m=1 skip.
total = 1+2 = 3. matches.

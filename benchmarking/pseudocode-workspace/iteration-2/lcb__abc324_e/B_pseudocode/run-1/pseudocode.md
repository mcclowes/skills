# Plan: count pairs where S_i + S_j contains T as subsequence

Verdict: logic-heavy (subsequence matching + counting via prefix/suffix decomposition). Plan first.

## Key idea
T (length L) is a subsequence of S_i + S_j iff there's a split point k (0..L) such that
T[0..k-1] is a subsequence of S_i AND T[k..L-1] is a subsequence of S_j.
Because matching greedily from the left through S_i then S_j, the maximum prefix
of T matched by S_i alone is some value a; whatever T-position we reach in S_i, S_j
must cover the rest. So pair works iff a + b >= L, where:
  a = f(S_i) = length of longest PREFIX of T that is a subsequence of S_i
  b = g(S_j) = length of longest SUFFIX of T that is a subsequence of S_j

Why a + b >= L is exactly the condition:
  - If a + b >= L: S_i matches T[0..a-1], and S_j matches the suffix of length b
    which is T[L-b..L-1]. Since a >= L-b (from a+b>=L), the suffix S_j matches
    covers from L-b <= a onward, i.e. it covers T[a..L-1]. So concatenation matches all of T.
  - If a + b < L: the best prefix from S_i ends before position a, and the best suffix
    S_j can supply starts at L-b > a, leaving gap T[a..L-b-1] uncovered. No split works.
    (Greedy prefix matching is optimal: matching as much prefix as possible in S_i never
     hurts what remains for S_j, since remaining is a contiguous suffix.)

## Data & invariants
- T: string length L >= 1.
- For each S_i compute:
    a_i = f(S_i) in [0, L]   (prefix of T matched greedily)
    b_i = g(S_i) in [0, L]   (suffix of T matched greedily, scanning S_i forward, T backward)
- Answer = number of ordered pairs (i,j) with a_i + b_j >= L. i and j range independently
  over 1..N (i==j allowed; problem says N^2 pairs).
- Invariant: a_i, b_i computed independently per string; total work O(total |S| ).

## Control flow

f(s): greedy prefix match
  p = 0
  for ch in s:
    if p < L and ch == T[p]: p += 1
  return p

g(s): greedy suffix match (match T from the end while scanning s from the end,
      OR scan s forward matching a reversed problem — simpler: scan s from right,
      track q = number of suffix chars matched)
  q = 0                     # matched T[L-1], T[L-2], ... so far q chars => matched suffix T[L-q..L-1]
  for ch in reversed(s):
    if q < L and ch == T[L-1-q]: q += 1
  return q

Main:
  read N, T; L = len(T)
  collect A = [f(S_i) for all i], B = [g(S_i) for all i]
  Count pairs with A[i] + B[j] >= L.
  Efficient counting (N up to 5e5, can't do O(N^2)):
    cntB[v] = number of j with B[j] == v, for v in 0..L
    suffixB[t] = number of j with B[j] >= t  (so suffixB[t] = cntB[t] + suffixB[t+1])
    answer = sum over i of suffixB[ max(0, L - A[i]) ]
      because need B[j] >= L - A[i]; if L - A[i] <= 0 then all N qualify (suffixB[0] = N).

## Edge cases
- L == 1: a_i is 0 or 1, b_i is 0 or 1. Pair works iff a_i+b_j>=1, i.e. at least one of them
  contains the single char. Handled by general formula.
- T longer than any concatenation: a_i + b_j may never reach L -> contributes 0. Handled.
- A[i] == L already (S_i alone contains T): need B[j] >= 0 -> all j. suffixB[0]=N. Correct
  (matches sample 2: every "x"+"x"="xx" contains "xx"? a_i for "x" vs T="xx": matches T[0]='x'
   -> a=1. b for "x": matches T[1]='x' -> b=1. 1+1=2>=2 -> all 25 pairs. Correct.)
- Sample 3: T="y", S="x": a=0,b=0, 0+0<1 -> 0. Correct.
- threshold L - A[i] could exceed L (no, A[i]>=0 so threshold<=L) or be negative (clamp to 0).
- suffixB indexed 0..L inclusive; size L+1, plus guard suffixB[L+1]=0.

## Contract
- Input via stdin in given format. Output single integer (the count) to stdout.
- Use fast IO (sys.stdin) due to up to 5e5 lines / 5e5 total chars.
- Counts can be up to N^2 = 2.5e11 -> needs 64-bit; Python int is fine.

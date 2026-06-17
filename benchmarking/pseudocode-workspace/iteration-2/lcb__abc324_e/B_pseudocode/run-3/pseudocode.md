# Count pairs (i,j) where S_i + S_j contains T as a subsequence

## Key idea
Concatenation S_i ++ S_j contains T as a subsequence iff:
  some prefix T[0..k) is a subsequence of S_i, and the remaining suffix T[k..|T|) is a subsequence of S_j.
The optimal split is greedy: let
  front[i] = max number of leading chars of T matchable as a subsequence of S_i (greedy from front)
  back[j]  = max number of trailing chars of T matchable as a subsequence of S_j (greedy from back)
Then (i,j) works iff front[i] + back[j] >= |T|.
(Greedy matching is optimal for "longest prefix of T that is a subsequence of S".)

## Data & invariants
- T: target string, length m (m >= 1).
- For each string S: front_count in [0, m], back_count in [0, m].
- Invariant: front_count = greedy match of T from index 0 advancing through S left-to-right.
- Invariant: back_count = greedy match of T from index m-1 advancing through S right-to-left.
- front[i] + back[j] >= m is the exact condition (proof: pick split at k = front[i]; if front[i] >= m already trivially true; else suffix needs m-front[i] <= back[j]).

## Control flow
m = len(T)
front_match(S):
  p = 0                      # next index of T to match
  for c in S left to right:
    if p < m and c == T[p]: p += 1
  return p                   # = how many leading chars of T matched

back_match(S):
  q = 0                      # how many trailing chars matched
  for c in S right to left:
    if q < m and c == T[m-1-q]: q += 1
  return q

Compute front[i] for all i, back[j] for all j.
We need count of ordered pairs (i,j) with front[i] + back[j] >= m.

Approach: build cnt_back[v] = number of j with back[j] == v, for v in 0..m.
Build suffix sum SB[t] = number of j with back[j] >= t.
  SB[t] for t<=0 is N; for t>m is 0.
For each i: needed = m - front[i]; add SB[max(needed,0)] (clamp: if needed<=0 → all N).
Sum over i = answer.

## Edge cases
- front[i] could be m (S_i alone contains T) → needed = 0 → all N values of j count (SB[0] = N).
- back[j] could be m → counts toward any i with front[i] >= 0, i.e. needed - any; handled by SB.
- m larger than any single string: still fine, counts may be 0.
- needed > m impossible since front>=0 so needed<=m; SB index in [0,m].
- Self pairs (i,i) are allowed and counted (N^2 pairs include i=j) — no exclusion.
- Answer can be up to N^2 = 2.5e11 → use 64-bit / Python int (no overflow in Python).
- Total length of all S <= 5e5, so per-string scans are O(total length) overall.

## Interface contract
- Read N and T from first line, then N strings.
- Output single integer: number of ordered pairs (i,j), 1<=i,j<=N, satisfying condition.
- Pure computation; reads stdin, writes stdout.

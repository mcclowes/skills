# ABC324 E — count pairs (i,j) where S_i+S_j contains T as subsequence

## Data & invariants
- T: target string, length m (1..5e5).
- For each S_i:
  - pref[i] = max chars of T matched greedily as subsequence by scanning S_i left→right
             against T left→right (0..m).
  - suf[i]  = max chars of T matched greedily as subsequence by scanning S_i right→left
             against T right→left (0..m). Equivalently, longest suffix of T that is a
             subsequence of S_i.
- Invariant: a concatenation S_i+S_j contains T iff we can split T into a prefix consumed
  by S_i and the remaining suffix consumed by S_j. Greedy matching is optimal for
  subsequence: matching as much of T's prefix as possible in S_i never hurts, because
  any split point covered by (pref[i], suf[j]) covering all of T means
  pref[i] + suf[j] >= m. (Greedy prefix uses the earliest chars, leaving the rest for S_j;
  if some split works then pref[i] (which is the maximum prefix) plus suf[j] (max suffix)
  must reach m.)

## Why pref[i] + suf[j] >= m is the exact condition
- If S_i covers a prefix of length p of T and S_j covers the remaining suffix of length m-p,
  pairing works. The best S_i can do for any prefix is pref[i]; best S_j for any suffix is
  suf[j]. A valid split of length p exists with p <= pref[i] and (m-p) <= suf[j], i.e.
  m - suf[j] <= p <= pref[i]. Such integer p in [0,m] exists iff
  m - suf[j] <= pref[i], i.e. pref[i] + suf[j] >= m.

## Control flow
1. Read N, T; m = len(T).
2. For each i:
   - greedy forward: k=0; for c in S_i: if k<m and c==T[k]: k+=1. pref[i]=k.
   - greedy backward: k=0; for c in reversed(S_i): if k<m and c==T[m-1-k]: k+=1. suf[i]=k.
3. Build freq array cnt[s] for s in 0..m of how many i have suf[i]==s.
4. Build suffix-sum: ge[t] = number of j with suf[j] >= t, for t in 0..m+ (clamp negatives→all N).
5. answer = 0; for each i: need = m - pref[i]; if need <= 0 → add N (all j work);
   else add ge[need].
6. Print answer.

## Edge cases & failure modes
- pref[i] == m  → S_i alone contains T → every j valid → add N. Covered by need<=0.
- need could be negative (pref>m impossible since capped at m, but pref==m gives need 0). Use need<=0 → N.
- need > m impossible since pref>=0 → need<=m; ge defined on 0..m.
- ge[0] = N (every suf>=0).
- T length 1 handled normally.
- Large input: total length sum <= 5e5, so O(total + N + m) work; counting answer up to N^2=2.5e11 → use Python int (fine).
- Output single integer.

## Interface contract
- Input via stdin in given format. Output: one integer (the count). No mutation concerns.

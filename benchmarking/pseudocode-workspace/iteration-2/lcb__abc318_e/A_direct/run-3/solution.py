import sys
from collections import defaultdict


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = [int(x) for x in data[1:1 + n]]

    pos = defaultdict(list)
    for idx, v in enumerate(a):
        pos[v].append(idx)

    ans = 0
    for v, ps in pos.items():
        m = len(ps)
        if m < 2:
            continue
        # Sum over all pairs (i, k) with i<k of (number of indices strictly
        # between them) minus (number of same-value indices strictly between).
        # gaps[t] = ps[t+1] - ps[t] - 1 = count of other-value-or-any indices
        # strictly between consecutive occurrences.
        # Total between any pair = sum of gaps in span + (count of same-value
        # occurrences strictly between). We want only different values, so:
        # different_between(i,k) = (ps[k]-ps[i]-1) - (k-i-1)
        # = (ps[k]-ps[i]) - (k-i)
        # Sum over pairs s<t of (ps[t]-ps[s]) - (t-s).
        # sum (ps[t]-ps[s]) = sum_t ps[t]*t_count_as_high - sum_s ps[s]*...
        # Compute via prefix.
        # For each t, contribution sum_{s<t} (ps[t]-ps[s]) - (t-s)
        prefix_pos = 0
        prefix_idx = 0
        total = 0
        for t in range(m):
            # pairs where t is the higher index, s ranges 0..t-1
            total += ps[t] * t - prefix_pos
            total -= t * t - prefix_idx
            prefix_pos += ps[t]
            prefix_idx += t
        ans += total

    print(ans)


if __name__ == "__main__":
    main()

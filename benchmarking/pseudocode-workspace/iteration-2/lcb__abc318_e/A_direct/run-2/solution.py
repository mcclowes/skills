import sys
from collections import defaultdict


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = [int(x) for x in data[1:1 + n]]

    # Group positions by value
    pos = defaultdict(list)
    for idx, v in enumerate(a):
        pos[v].append(idx)

    ans = 0
    for v, ps in pos.items():
        m = len(ps)
        if m < 2:
            continue
        # For each pair (i, k) of equal values, count of j between them
        # equals (k - i - 1) - (number of equal-value positions strictly between).
        # Sum over all pairs:
        #   sum_{a<b} (ps[b] - ps[a] - 1)  : raw gap count
        # minus sum over pairs of equal positions strictly between.
        #
        # Raw gap: sum_{a<b} (ps[b] - ps[a]) - C(m,2)
        # sum_{a<b}(ps[b]-ps[a]) = sum_t ps[t]*(t - (m-1-t)) = sum_t ps[t]*(2t-(m-1))
        gap_sum = 0
        for t in range(m):
            gap_sum += ps[t] * (2 * t - (m - 1))
        pairs = m * (m - 1) // 2
        raw = gap_sum - pairs

        # Equal-value positions strictly between ps[a] and ps[b]:
        # for a pair (a, b) with a < b, that's (b - a - 1) positions of same value.
        # Sum over pairs = sum_{a<b}(b-a-1) = sum over indices treated as 0..m-1
        # which equals C(m,3) ? Let's compute: sum_{a<b}(b-a-1).
        # = sum_{d=1}^{m-1} (d-1)*(m-d) where d=b-a
        same_between = 0
        for d in range(1, m):
            same_between += (d - 1) * (m - d)

        ans += raw - same_between

    print(ans)


main()

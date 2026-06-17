import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = data[1:1 + n]

    cnt = {}
    sum_idx = {}
    gap_total = 0

    # positions 1-based; for each k, pairs (i, k) with A_i == A_k == v
    # contribute (k - i - 1) summed over earlier i.
    for pos in range(1, n + 1):
        v = a[pos - 1]
        c = cnt.get(v, 0)
        s = sum_idx.get(v, 0)
        # sum over earlier equal positions i of (pos - i - 1)
        gap_total += c * pos - s - c
        cnt[v] = c + 1
        sum_idx[v] = s + pos

    # subtract triples where the middle index also equals v: C(m, 3) per value
    bad = 0
    for m in cnt.values():
        if m >= 3:
            bad += m * (m - 1) * (m - 2) // 6

    print(gap_total - bad)


main()

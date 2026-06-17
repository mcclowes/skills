import sys
from bisect import bisect_right


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    t = data[1].decode()
    m = len(t)
    strings = [data[2 + i].decode() for i in range(n)]

    # For each S, prefix = how many chars of T (from start) matched greedily
    # suffix = how many chars of T (from end) matched greedily reading S backwards
    prefix_counts = [0] * (m + 1)
    suffix_list = []

    for s in strings:
        # prefix match
        p = 0
        for c in s:
            if p < m and c == t[p]:
                p += 1
        prefix_counts[p] += 1

        # suffix match
        q = m
        for c in reversed(s):
            if q > 0 and c == t[q - 1]:
                q -= 1
        suffix_list.append(m - q)  # number matched from the end

    suffix_list.sort()

    ans = 0
    # for each prefix value p (from a string i), count strings j with suffix >= m - p
    # iterate over prefix_counts
    for p in range(m + 1):
        cnt = prefix_counts[p]
        if cnt == 0:
            continue
        need = m - p
        if need <= 0:
            ans += cnt * n
        else:
            # number of suffix values >= need
            idx = bisect_right(suffix_list, need - 1)
            ans += cnt * (n - idx)

    print(ans)


main()

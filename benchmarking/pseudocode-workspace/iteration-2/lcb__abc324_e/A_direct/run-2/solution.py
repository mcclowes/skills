import sys
from bisect import bisect_left


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    t = data[idx].decode(); idx += 1
    m = len(t)

    prefix_counts = [0] * (m + 1)  # how many S have prefix-match == k
    suffix_vals = []               # suffix-match values for all S

    for _ in range(n):
        s = data[idx].decode(); idx += 1

        # prefix: greedily match T from front
        a = 0
        for c in s:
            if a < m and c == t[a]:
                a += 1
        prefix_counts[a] += 1

        # suffix: greedily match T from back
        b = 0
        for c in reversed(s):
            if b < m and c == t[m - 1 - b]:
                b += 1
        suffix_vals.append(b)

    # prefix_total[k] = number of S with prefix-match >= k
    suffix_vals.sort()
    sv = suffix_vals
    ns = len(sv)

    ans = 0
    # for each prefix value a (with count), count j with b_j >= m - a
    for a in range(m + 1):
        c = prefix_counts[a]
        if c == 0:
            continue
        need = m - a
        if need <= 0:
            cnt = ns
        else:
            pos = bisect_left(sv, need)
            cnt = ns - pos
        ans += c * cnt

    sys.stdout.write(str(ans) + "\n")


main()

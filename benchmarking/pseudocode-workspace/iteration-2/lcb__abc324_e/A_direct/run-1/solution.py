import sys
from bisect import bisect_left


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    t = data[idx].decode(); idx += 1
    m = len(t)

    pres = []
    sufs = []
    for _ in range(n):
        s = data[idx].decode(); idx += 1
        # longest prefix of t matchable as subsequence of s
        p = 0
        for ch in s:
            if p < m and ch == t[p]:
                p += 1
        pres.append(p)
        # longest suffix of t matchable as subsequence of s
        q = m - 1
        for ch in reversed(s):
            if q >= 0 and ch == t[q]:
                q -= 1
        sufs.append(m - 1 - q)

    sufs.sort()
    ans = 0
    for p in pres:
        # need suf >= m - p
        need = m - p
        # count sufs >= need
        ans += len(sufs) - bisect_left(sufs, need)

    sys.stdout.write(str(ans) + "\n")


main()

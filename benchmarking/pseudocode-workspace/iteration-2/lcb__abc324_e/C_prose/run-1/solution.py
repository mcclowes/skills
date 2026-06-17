import sys
from bisect import bisect_left


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    t = data[1].decode()
    strings = [data[2 + i].decode() for i in range(n)]

    m = len(t)

    pref = []  # longest prefix of t matchable in each string
    suf = []   # longest suffix of t matchable in each string

    for s in strings:
        # greedy front match
        p = 0
        for ch in s:
            if p < m and ch == t[p]:
                p += 1
        pref.append(p)

        # greedy back match
        q = 0  # number of trailing chars of t matched
        for ch in reversed(s):
            if q < m and ch == t[m - 1 - q]:
                q += 1
        suf.append(q)

    suf.sort()
    total = 0
    for a in pref:
        need = m - a
        if need <= 0:
            total += n
        else:
            # count b_j with b_j >= need
            idx = bisect_left(suf, need)
            total += n - idx

    sys.stdout.write(str(total) + "\n")


main()

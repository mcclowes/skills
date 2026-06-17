import sys


def main():
    data = sys.stdin.buffer.read().split(b"\n")
    first = data[0].split()
    n = int(first[0])
    t = first[1]
    m = len(t)

    # cnt[s] = number of strings whose suffix-match length is s
    cnt = [0] * (m + 1)
    # accumulate answer contribution from pref later; first collect prefs
    prefs = []

    idx = 1
    for _ in range(n):
        s = data[idx]
        idx += 1

        # greedy forward prefix match
        k = 0
        for c in s:
            if k < m and c == t[k]:
                k += 1
        prefs.append(k)

        # greedy backward suffix match
        k2 = 0
        for c in reversed(s):
            if k2 < m and c == t[m - 1 - k2]:
                k2 += 1
        cnt[k2] += 1

    # ge[v] = number of j with suf[j] >= v, for v in 0..m
    ge = [0] * (m + 2)
    running = 0
    for v in range(m, -1, -1):
        running += cnt[v]
        ge[v] = running
    # ge[m+1] = 0

    ans = 0
    for p in prefs:
        need = m - p
        if need <= 0:
            ans += n
        else:
            ans += ge[need]

    sys.stdout.write(str(ans) + "\n")


main()

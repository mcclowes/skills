import sys


def main():
    data = sys.stdin.buffer.read().split()
    # data[0] = N, data[1] = T, data[2..] = S_i
    n = int(data[0])
    t = data[1].decode()
    m = len(t)

    strings = data[2:2 + n]

    # cnt_back[v] = number of j with back_match == v
    cnt_back = [0] * (m + 1)

    front_counts = []

    for raw in strings:
        s = raw.decode()

        # front: longest prefix of T matchable as subsequence of s
        p = 0
        for c in s:
            if p < m and c == t[p]:
                p += 1
        front_counts.append(p)

        # back: longest suffix of T matchable as subsequence of s (scan right-to-left)
        q = 0
        for c in reversed(s):
            if q < m and c == t[m - 1 - q]:
                q += 1
        cnt_back[q] += 1

    # SB[k] = number of j with back >= k, for k in 0..m
    # SB[0] = n (all)
    sb = [0] * (m + 2)
    running = 0
    for v in range(m, -1, -1):
        running += cnt_back[v]
        sb[v] = running
    # sb[k] for k from 0..m holds count of back >= k. k=0 -> n.

    ans = 0
    for fr in front_counts:
        needed = m - fr
        if needed <= 0:
            ans += n
        else:
            ans += sb[needed]

    sys.stdout.write(str(ans) + "\n")


main()

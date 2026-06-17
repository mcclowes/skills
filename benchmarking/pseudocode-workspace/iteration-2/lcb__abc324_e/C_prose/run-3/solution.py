import sys


def main():
    data = sys.stdin.buffer.read().split(b"\n")
    first = data[0].split()
    n = int(first[0])
    t = first[1]
    L = len(t)

    # prefix(S): largest k such that t[:k] is a subsequence of S
    def prefix_match(s):
        p = 0
        for c in s:
            if p < L and c == t[p]:
                p += 1
        return p

    # suffix(S): largest m such that t[L-m:] is a subsequence of S
    def suffix_match(s):
        p = L
        for i in range(len(s) - 1, -1, -1):
            if p > 0 and s[i] == t[p - 1]:
                p -= 1
        return L - p

    a_vals = []
    # count[b] = number of strings with suffix_match == b, b in 0..L
    cnt = [0] * (L + 1)

    for idx in range(1, n + 1):
        s = data[idx]
        a_vals.append(prefix_match(s))
        b = suffix_match(s)
        cnt[b] += 1

    # suffix sums: suf[v] = number of strings with b >= v
    suf = [0] * (L + 2)
    for v in range(L, -1, -1):
        suf[v] = suf[v + 1] + cnt[v]

    ans = 0
    for a in a_vals:
        need = L - a
        if need <= 0:
            ans += n
        else:
            ans += suf[need]

    sys.stdout.write(str(ans) + "\n")


main()

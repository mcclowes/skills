import sys


def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    n = int(data[0])
    t = data[1].decode()
    m = len(t)
    strings = data[2:2 + n]

    # atleast[k] will hold count of j with suf[j] >= k, built later.
    # First collect frequencies of suf values and accumulate pre contributions.
    suf_count = [0] * (m + 1)
    pre_vals = []

    for raw in strings:
        s = raw.decode()

        # prefix match: how much of T's front S consumes greedily
        p = 0
        for ch in s:
            if p < m and ch == t[p]:
                p += 1
        pre_vals.append(p)

        # suffix match: how much of T's back S consumes greedily
        q = m  # pointer into t, matching from index q-1 downward
        for ch in reversed(s):
            if q > 0 and ch == t[q - 1]:
                q -= 1
        suf = m - q
        suf_count[suf] += 1

    # atleast[k] = number of j with suf[j] >= k
    atleast = [0] * (m + 2)
    for k in range(m, -1, -1):
        atleast[k] = atleast[k + 1] + suf_count[k]

    ans = 0
    for p in pre_vals:
        need = m - p
        if need < 0:
            need = 0
        ans += atleast[need]

    sys.stdout.write(str(ans) + "\n")


main()

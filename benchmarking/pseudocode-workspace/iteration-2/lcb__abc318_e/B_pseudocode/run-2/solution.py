import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = data[1:1 + n]

    positions = {}
    for idx in range(n):
        v = a[idx]
        positions.setdefault(v, []).append(idx)

    ans = 0
    for p in positions.values():
        m = len(p)
        if m < 2:
            continue
        prefix = 0
        pairgap = 0
        for b in range(m):
            pairgap += p[b] * b - prefix
            prefix += p[b]
        numpairs = m * (m - 1) // 2
        term1 = pairgap - numpairs
        term2 = 0
        for c in range(m):
            cc = c + 1
            term2 += (cc - 1) * (m - cc)
        ans += term1 - term2

    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()

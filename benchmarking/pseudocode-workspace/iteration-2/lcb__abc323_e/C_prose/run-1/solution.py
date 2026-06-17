import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    x = int(data[1])
    t = [int(v) for v in data[2:2 + n]]

    MOD = 998244353
    invN = pow(n, MOD - 2, MOD)

    # start[s] = probability some song begins exactly at integer time s.
    start = [0] * (x + 1)
    start[0] = 1
    for s in range(1, x + 1):
        acc = 0
        for ti in t:
            if ti <= s:
                acc += start[s - ti]
        start[s] = (acc % MOD) * invN % MOD

    t1 = t[0]
    lo = max(0, x - t1 + 1)
    total = 0
    for s in range(lo, x + 1):
        total += start[s]
    ans = total % MOD * invN % MOD
    print(ans)


if __name__ == "__main__":
    main()

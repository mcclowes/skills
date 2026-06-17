import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    t = [int(data[idx + i]) for i in range(n)]
    idx += n

    MOD = 998244353
    invN = pow(n, MOD - 2, MOD)

    dp = [0] * (x + 1)
    dp[0] = 1
    for cur in range(x + 1):
        d = dp[cur]
        if d == 0:
            continue
        d = d * invN % MOD
        for ti in t:
            nt = cur + ti
            if nt <= x:
                dp[nt] = (dp[nt] + d) % MOD

    t1 = t[0]
    lo = max(0, x - t1 + 1)
    ans = 0
    for s in range(lo, x + 1):
        ans = (ans + dp[s] * invN) % MOD

    print(ans % MOD)


if __name__ == "__main__":
    main()

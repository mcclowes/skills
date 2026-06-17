import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    X = int(data[idx]); idx += 1
    T = [int(data[idx + i]) for i in range(N)]

    MOD = 998244353
    invN = pow(N, MOD - 2, MOD)

    dp = [0] * (X + 1)
    dp[0] = 1
    for t in range(1, X + 1):
        acc = 0
        for ti in T:
            if t - ti >= 0:
                acc += dp[t - ti]
        dp[t] = (acc % MOD) * invN % MOD

    T1 = T[0]
    lo = max(0, X + 1 - T1)
    ans = 0
    for s in range(lo, X + 1):
        ans += dp[s] * invN
    ans %= MOD
    print(ans)


if __name__ == "__main__":
    main()

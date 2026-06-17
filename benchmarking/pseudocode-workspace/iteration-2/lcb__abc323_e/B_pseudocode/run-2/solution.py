import sys


def main():
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    t = [int(data[idx + i]) for i in range(n)]

    MOD = 998244353
    inv_n = pow(n, MOD - 2, MOD)

    dp = [0] * (x + 1)
    dp[0] = 1
    for time in range(1, x + 1):
        s = 0
        for d in t:
            if time - d >= 0:
                s += dp[time - d]
        dp[time] = (s % MOD) * inv_n % MOD

    ans = 0
    lo = max(0, x - t[0] + 1)
    for st in range(lo, x + 1):
        ans = (ans + dp[st] * inv_n) % MOD

    print(ans)


if __name__ == "__main__":
    main()

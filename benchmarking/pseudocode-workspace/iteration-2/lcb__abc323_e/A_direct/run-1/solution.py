import sys

MOD = 998244353

def main():
    data = sys.stdin.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    X = int(data[idx]); idx += 1
    T = [int(data[idx + i]) for i in range(N)]

    invN = pow(N, MOD - 2, MOD)

    # dp[t] = probability that a song boundary (new song starts) occurs at time t
    dp = [0] * (X + 1)
    dp[0] = 1
    for t in range(1, X + 1):
        s = 0
        for ti in T:
            if t - ti >= 0:
                s += dp[t - ti]
        dp[t] = (s * invN) % MOD

    t1 = T[0]
    lo = max(0, X - t1 + 1)
    ans = 0
    for s in range(lo, X + 1):
        ans = (ans + dp[s]) % MOD
    ans = (ans * invN) % MOD
    print(ans)

main()

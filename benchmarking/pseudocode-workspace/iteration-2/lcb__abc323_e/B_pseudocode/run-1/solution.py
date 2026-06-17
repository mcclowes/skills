import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    X = int(data[idx]); idx += 1
    T = [int(data[idx + i]) for i in range(N)]
    MOD = 998244353

    invN = pow(N, MOD - 2, MOD)

    # dp[t] = probability that a song boundary (some song starts) at integer time t
    dp = [0] * (X + 1)
    dp[0] = 1
    for t in range(1, X + 1):
        acc = 0
        for ti in T:
            p = t - ti
            if p >= 0:
                acc += dp[p]
        dp[t] = (acc % MOD) * invN % MOD

    # Song 1 playing at X+0.5 iff song 1 started at t in [X-T1+1 .. X]
    T1 = T[0]
    lo = max(0, X - T1 + 1)
    s = 0
    for t in range(lo, X + 1):
        s += dp[t]
    ans = (s % MOD) * invN % MOD
    print(ans % MOD)


main()

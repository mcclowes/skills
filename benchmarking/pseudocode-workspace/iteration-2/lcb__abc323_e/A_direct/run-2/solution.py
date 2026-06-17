import sys


def main():
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    t = [int(data[idx + i]) for i in range(n)]
    idx += n

    MOD = 998244353
    inv_n = pow(n, MOD - 2, MOD)

    # dp[s] = probability that a song boundary (start of a new song) occurs exactly at time s
    # dp[0] = 1 (a song starts at time 0)
    dp = [0] * (x + 1)
    dp[0] = 1
    for s in range(1, x + 1):
        acc = 0
        for ti in t:
            if s - ti >= 0:
                acc += dp[s - ti]
        dp[s] = (acc % MOD) * inv_n % MOD

    # Song 1 is playing at time X+0.5 if a song starts at time s (0 <= s <= X)
    # that song is song 1 (prob 1/N), and it lasts long enough: s + T_1 > X + 0.5,
    # i.e. s + T_1 >= X + 1, i.e. s >= X + 1 - T_1.
    t1 = t[0]
    ans = 0
    lo = max(0, x + 1 - t1)
    for s in range(lo, x + 1):
        ans = (ans + dp[s]) % MOD
    ans = ans * inv_n % MOD

    print(ans)


main()

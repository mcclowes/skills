import sys

MOD = 998244353


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    t = [int(data[idx + i]) for i in range(n)]

    inv_n = pow(n, MOD - 2, MOD)

    # dp[s] = probability a song boundary (new song start) occurs at time s
    dp = [0] * (x + 1)
    dp[0] = 1
    for s in range(x + 1):
        if dp[s] == 0:
            continue
        cur = dp[s] * inv_n % MOD
        for tj in t:
            ns = s + tj
            if ns <= x:
                dp[ns] = (dp[ns] + cur) % MOD

    # A play of song 1 starting at boundary time s covers X+0.5 iff
    # X - T_1 + 1 <= s <= X.
    t1 = t[0]
    lo = max(0, x - t1 + 1)
    ans = 0
    for s in range(lo, x + 1):
        ans = (ans + dp[s] * inv_n) % MOD

    print(ans % MOD)


if __name__ == "__main__":
    main()

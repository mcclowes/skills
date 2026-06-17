import sys

MOD = 998244353

def main():
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    t = [int(data[idx + i]) for i in range(n)]
    idx += n

    inv_n = pow(n, MOD - 2, MOD)

    # f[s] = probability that a song boundary (some song ends) occurs exactly at second s
    # f[0] = 1 (a song starts at time 0)
    # f[s] = sum over songs i with t_i <= s of f[s - t_i] * (1/n)
    f = [0] * (x + 1)
    f[0] = 1
    for s in range(1, x + 1):
        acc = 0
        for ti in t:
            if ti <= s:
                acc += f[s - ti]
        f[s] = acc % MOD * inv_n % MOD

    # song 1 is playing at time X+0.5 if it starts at second s (boundary at s,
    # then chosen song is song 1) with s <= X < s + t[0]
    # i.e. s in [max(0, X - t[0] + 1), X]
    t1 = t[0]
    lo = max(0, x - t1 + 1)
    ans = 0
    for s in range(lo, x + 1):
        ans = (ans + f[s]) % MOD
    ans = ans * inv_n % MOD

    print(ans)

main()

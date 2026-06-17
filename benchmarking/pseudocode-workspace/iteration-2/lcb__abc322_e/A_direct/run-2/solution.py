import sys


def main():
    data = sys.stdin.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    K = int(data[idx]); idx += 1
    P = int(data[idx]); idx += 1

    plans = []
    for _ in range(N):
        c = int(data[idx]); idx += 1
        a = [int(data[idx + j]) for j in range(K)]
        idx += K
        plans.append((c, a))

    # State: tuple of capped parameter values, each in [0, P]
    base = P + 1
    size = base ** K

    def encode(vals):
        s = 0
        for v in vals:
            s = s * base + v
        return s

    INF = float('inf')
    dp = [INF] * size
    dp[0] = 0

    for c, a in plans:
        new_dp = dp[:]
        for state in range(size):
            if dp[state] == INF:
                continue
            # decode
            vals = []
            t = state
            for _ in range(K):
                vals.append(t % base)
                t //= base
            vals.reverse()
            # apply plan
            nvals = [min(P, vals[j] + a[j]) for j in range(K)]
            ns = encode(nvals)
            cost = dp[state] + c
            if cost < new_dp[ns]:
                new_dp[ns] = cost
        dp = new_dp

    goal = encode([P] * K)
    ans = dp[goal]
    print(-1 if ans == INF else ans)


main()

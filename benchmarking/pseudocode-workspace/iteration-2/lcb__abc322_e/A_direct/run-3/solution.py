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
        a = [min(int(data[idx + j]), P) for j in range(K)]
        idx += K
        plans.append((c, a))

    INF = float('inf')
    size = (P + 1) ** K

    def encode(state):
        code = 0
        for v in state:
            code = code * (P + 1) + v
        return code

    dp = [INF] * size
    dp[0] = 0

    for c, a in plans:
        ndp = dp[:]
        for code in range(size):
            if dp[code] == INF:
                continue
            # decode
            vals = []
            tmp = code
            for _ in range(K):
                vals.append(tmp % (P + 1))
                tmp //= (P + 1)
            vals.reverse()
            new_vals = [min(vals[j] + a[j], P) for j in range(K)]
            ncode = encode(new_vals)
            cost = dp[code] + c
            if cost < ndp[ncode]:
                ndp[ncode] = cost
        dp = ndp

    goal = encode([P] * K)
    ans = dp[goal]
    print(ans if ans != INF else -1)


main()

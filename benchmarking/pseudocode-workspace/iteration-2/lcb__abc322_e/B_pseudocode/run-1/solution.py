import sys


def main():
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    k = int(data[idx]); idx += 1
    p = int(data[idx]); idx += 1

    plans = []
    for _ in range(n):
        c = int(data[idx]); idx += 1
        a = [int(data[idx + j]) for j in range(k)]
        idx += k
        plans.append((c, a))

    INF = float('inf')
    start = tuple([0] * k)
    goal = tuple([p] * k)

    dp = {start: 0}

    for c, a in plans:
        new_dp = dict(dp)
        for s, cost in dp.items():
            ns = tuple(min(s[j] + a[j], p) for j in range(k))
            cand = cost + c
            if cand < new_dp.get(ns, INF):
                new_dp[ns] = cand
        dp = new_dp

    ans = dp.get(goal, INF)
    print(-1 if ans == INF else ans)


if __name__ == "__main__":
    main()

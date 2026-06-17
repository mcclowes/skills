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
        a = tuple(int(data[idx + j]) for j in range(k))
        idx += k
        plans.append((c, a))

    start = tuple([0] * k)
    INF = float("inf")
    dp = {start: 0}

    for c, a in plans:
        next_dp = dict(dp)  # option: do not take this plan
        for state, cost in dp.items():
            ns = tuple(min(state[j] + a[j], p) for j in range(k))
            new_cost = cost + c
            if new_cost < next_dp.get(ns, INF):
                next_dp[ns] = new_cost
        dp = next_dp

    goal = tuple([p] * k)
    ans = dp.get(goal, INF)
    print(ans if ans != INF else -1)


if __name__ == "__main__":
    main()

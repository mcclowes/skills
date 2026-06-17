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
        gains = tuple(int(data[idx + j]) for j in range(k))
        idx += k
        plans.append((c, gains))

    start = tuple([0] * k)
    target = tuple([p] * k)
    dp = {start: 0}

    for c, gains in plans:
        for state, cost in list(dp.items()):
            new_state = tuple(min(p, state[j] + gains[j]) for j in range(k))
            new_cost = cost + c
            if new_state not in dp or new_cost < dp[new_state]:
                dp[new_state] = new_cost

    print(dp[target] if target in dp else -1)


if __name__ == "__main__":
    main()

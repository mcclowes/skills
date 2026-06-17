import sys


def main():
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    k = int(data[idx]); idx += 1
    p = int(data[idx]); idx += 1

    plans = []
    for _ in range(n):
        cost = int(data[idx]); idx += 1
        incs = tuple(int(data[idx + j]) for j in range(k))
        idx += k
        plans.append((cost, incs))

    start = tuple([0] * k)
    full = tuple([p] * k)
    best = {start: 0}

    for cost, incs in plans:
        for state, cur in list(best.items()):
            new_state = tuple(min(p, state[j] + incs[j]) for j in range(k))
            new_cost = cur + cost
            if new_state not in best or new_cost < best[new_state]:
                best[new_state] = new_cost

    print(best.get(full, -1))


if __name__ == "__main__":
    main()

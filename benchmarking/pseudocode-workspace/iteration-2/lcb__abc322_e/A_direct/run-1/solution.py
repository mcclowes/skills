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
        a = []
        for _ in range(k):
            a.append(int(data[idx])); idx += 1
        plans.append((c, a))

    base = p + 1
    num_states = base ** k
    INF = float('inf')
    dp = [INF] * num_states
    dp[0] = 0  # all parameters at 0

    def encode(vals):
        s = 0
        for v in vals:
            s = s * base + v
        return s

    def decode(state):
        vals = [0] * k
        for i in range(k - 1, -1, -1):
            vals[i] = state % base
            state //= base
        return vals

    for c, a in plans:
        new_dp = dp[:]
        for state in range(num_states):
            if dp[state] == INF:
                continue
            vals = decode(state)
            new_vals = [min(p, vals[j] + a[j]) for j in range(k)]
            ns = encode(new_vals)
            cost = dp[state] + c
            if cost < new_dp[ns]:
                new_dp[ns] = cost
        dp = new_dp

    target = encode([p] * k)
    ans = dp[target]
    print(ans if ans != INF else -1)


main()

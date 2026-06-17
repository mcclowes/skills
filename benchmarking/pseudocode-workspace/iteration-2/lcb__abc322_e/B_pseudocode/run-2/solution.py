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

    base = p + 1
    num_states = base ** k
    INF = float('inf')

    # Precompute, for each state index, its digit representation.
    def to_digits(s):
        digits = []
        for _ in range(k):
            digits.append(s % base)
            s //= base
        return digits

    digits_cache = [to_digits(s) for s in range(num_states)]
    target = num_states - 1  # all params == p

    dp = [INF] * num_states
    dp[0] = 0

    for c, a in plans:
        new_dp = dp[:]
        for s in range(num_states):
            cur = dp[s]
            if cur == INF:
                continue
            d = digits_cache[s]
            ns = 0
            mult = 1
            for j in range(k):
                nv = d[j] + a[j]
                if nv > p:
                    nv = p
                ns += nv * mult
                mult *= base
            cand = cur + c
            if cand < new_dp[ns]:
                new_dp[ns] = cand
        dp = new_dp

    ans = dp[target]
    print(-1 if ans == INF else ans)


if __name__ == "__main__":
    main()

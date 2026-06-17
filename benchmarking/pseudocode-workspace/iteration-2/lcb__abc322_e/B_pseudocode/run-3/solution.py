import sys


def main():
    data = sys.stdin.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    K = int(data[idx]); idx += 1
    P = int(data[idx]); idx += 1

    plans = []
    for _ in range(N):
        C = int(data[idx]); idx += 1
        A = [int(data[idx + j]) for j in range(K)]
        idx += K
        plans.append((C, A))

    base = P + 1
    num_states = base ** K
    INF = float('inf')

    # Precompute component values for each state for fast capping.
    dp = [INF] * num_states
    dp[0] = 0  # zero-state

    goal = num_states - 1  # all components = P

    for C, A in plans:
        new_dp = dp[:]  # not taking this plan
        for s in range(num_states):
            cur = dp[s]
            if cur == INF:
                continue
            # decode s, add A, cap at P, encode next
            rem = s
            nxt = 0
            mult = 1
            for j in range(K):
                comp = rem % base
                rem //= base
                ncomp = comp + A[j]
                if ncomp > P:
                    ncomp = P
                nxt += ncomp * mult
                mult *= base
            cand = cur + C
            if cand < new_dp[nxt]:
                new_dp[nxt] = cand
        dp = new_dp

    ans = dp[goal]
    print(-1 if ans == INF else ans)


if __name__ == "__main__":
    main()

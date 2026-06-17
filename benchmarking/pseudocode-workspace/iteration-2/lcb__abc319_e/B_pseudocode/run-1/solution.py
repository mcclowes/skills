import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    y = int(data[idx]); idx += 1

    P = [0] * (n - 1)
    T = [0] * (n - 1)
    for i in range(n - 1):
        P[i] = int(data[idx]); idx += 1
        T[i] = int(data[idx]); idx += 1

    L = 840  # lcm(1..8); each P_i divides 840

    # delta[r] = total time added traversing all buses if arriving at stop 1
    # at a time t with t % 840 == r. end - start is invariant across the class.
    delta = [0] * L
    for r in range(L):
        t = r
        for i in range(n - 1):
            p = P[i]
            m = t % p
            if m:
                t += p - m
            t += T[i]
        delta[r] = t - r

    q_count = int(data[idx]); idx += 1
    out = []
    base = x + y
    for _ in range(q_count):
        q = int(data[idx]); idx += 1
        t1 = q + x
        out.append(q + base + delta[t1 % L])

    sys.stdout.write("\n".join(map(str, out)) + "\n")


if __name__ == "__main__":
    main()

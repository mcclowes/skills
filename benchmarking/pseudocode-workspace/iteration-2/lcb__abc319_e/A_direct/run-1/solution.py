import sys

def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    X = int(data[idx]); idx += 1
    Y = int(data[idx]); idx += 1
    P = [0] * (N - 1)
    T = [0] * (N - 1)
    for i in range(N - 1):
        P[i] = int(data[idx]); idx += 1
        T[i] = int(data[idx]); idx += 1

    L = 840  # lcm(1..8)

    # For each residue r in [0, L), compute total travel time from arriving
    # at bus stop 1 at a time congruent to r mod L, through to bus stop N.
    # Then answer for query q = q + X + travel(r) + Y, where r = (q + X) mod L.
    add = [0] * L
    for r in range(L):
        cur = r
        for i in range(N - 1):
            p = P[i]
            rem = cur % p
            if rem != 0:
                cur += (p - rem)
            cur += T[i]
        add[r] = cur - r  # total time spent from stop 1 to stop N

    out = []
    Q = int(data[idx]); idx += 1
    for _ in range(Q):
        q = int(data[idx]); idx += 1
        arrive1 = q + X
        r = arrive1 % L
        ans = arrive1 + add[r] + Y
        out.append(str(ans))

    sys.stdout.write("\n".join(out) + "\n")

main()

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

    L = 840
    # For each residue r mod 840 representing arrival time at bus stop 1,
    # compute total time to reach bus stop N.
    # We compute the offset added when starting at arrival time = r at stop 1.
    # add[r] = time to go from arrival at stop 1 (with arrival time congruent to r mod 840)
    #          to arrival at stop N.
    add = [0] * L
    for r in range(L):
        t = r
        for i in range(N - 1):
            # wait until next multiple of P[i]
            p = P[i]
            rem = t % p
            if rem != 0:
                t += p - rem
            t += T[i]
        add[r] = t - r

    Q = int(data[idx]); idx += 1
    out = []
    for _ in range(Q):
        q = int(data[idx]); idx += 1
        arrive1 = q + X
        r = arrive1 % L
        ans = arrive1 + add[r] + Y
        out.append(str(ans))

    sys.stdout.write("\n".join(out) + "\n")

main()

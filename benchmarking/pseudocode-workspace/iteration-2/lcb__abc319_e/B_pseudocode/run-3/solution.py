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
    add = [0] * L
    for r in range(L):
        t = r
        for i in range(N - 1):
            p = P[i]
            t = ((t + p - 1) // p) * p + T[i]
        add[r] = t - r

    Q = int(data[idx]); idx += 1
    out = []
    for _ in range(Q):
        q = int(data[idx]); idx += 1
        t1 = q + X
        tN = t1 + add[t1 % L]
        out.append(str(tN + Y))

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()

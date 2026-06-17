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

    LCM = 840
    f = [0] * LCM
    for r in range(LCM):
        t = r
        for i in range(N - 1):
            p = P[i]
            dep = ((t + p - 1) // p) * p
            t = dep + T[i]
        f[r] = t

    Q = int(data[idx]); idx += 1
    out = []
    for _ in range(Q):
        q = int(data[idx]); idx += 1
        A = q + X
        r = A % LCM
        ans = (A - r) + f[r] + Y
        out.append(str(ans))

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()

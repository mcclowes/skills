import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    y = int(data[idx]); idx += 1

    ps = []
    ts = []
    for _ in range(n - 1):
        p = int(data[idx]); idx += 1
        t = int(data[idx]); idx += 1
        ps.append(p)
        ts.append(t)

    L = 840  # lcm(1..8)

    # delta[r] = time to travel from stop 1 (arriving at a time congruent to r mod L)
    # all the way to stop N.
    delta = [0] * L
    for r in range(L):
        cur = r
        for i in range(n - 1):
            p = ps[i]
            # next departure: smallest multiple of p that is >= cur
            cur = ((cur + p - 1) // p) * p + ts[i]
        delta[r] = cur - r

    q = int(data[idx]); idx += 1
    out = []
    for _ in range(q):
        qi = int(data[idx]); idx += 1
        s = qi + x  # arrival time at stop 1
        ans = s + delta[s % L] + y
        out.append(str(ans))

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()

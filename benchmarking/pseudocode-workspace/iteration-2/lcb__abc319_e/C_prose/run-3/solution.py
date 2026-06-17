import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    x = int(data[idx]); idx += 1
    y = int(data[idx]); idx += 1

    buses = []
    for _ in range(n - 1):
        p = int(data[idx]); idx += 1
        t = int(data[idx]); idx += 1
        buses.append((p, t))

    L = 840
    # ans[r]: final arrival offset starting from stop 1 at time r (small r in [0,840))
    ans = [0] * L
    for r in range(L):
        cur = r
        for p, t in buses:
            # wait until next multiple of p
            cur = ((cur + p - 1) // p) * p
            cur += t
        cur += y
        ans[r] = cur

    q = int(data[idx]); idx += 1
    out = []
    for _ in range(q):
        qi = int(data[idx]); idx += 1
        t1 = qi + x
        r = t1 % L
        base = t1 - r
        out.append(str(base + ans[r]))

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()

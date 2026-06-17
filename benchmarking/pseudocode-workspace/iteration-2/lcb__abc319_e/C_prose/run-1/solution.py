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
        ps.append(int(data[idx])); idx += 1
        ts.append(int(data[idx])); idx += 1

    LCM = 840
    f = [0] * LCM
    for r in range(LCM):
        cur = r
        for i in range(n - 1):
            p = ps[i]
            cur = ((cur + p - 1) // p) * p
            cur += ts[i]
        f[r] = cur - r

    q = int(data[idx]); idx += 1
    out = []
    for _ in range(q):
        qi = int(data[idx]); idx += 1
        a = qi + x
        out.append(str(a + f[a % LCM] + y))

    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()

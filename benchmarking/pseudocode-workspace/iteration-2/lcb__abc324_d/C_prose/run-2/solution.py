import sys
import math


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1] if len(data) > 1 else ""

    target = sorted(s)
    limit = 10 ** n
    max_k = math.isqrt(limit - 1)

    count = 0
    for k in range(max_k + 1):
        sq = k * k
        padded = str(sq).zfill(n)
        if sorted(padded) == target:
            count += 1

    print(count)


if __name__ == "__main__":
    main()

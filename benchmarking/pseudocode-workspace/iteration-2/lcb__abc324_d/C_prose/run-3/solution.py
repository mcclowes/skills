import sys
from collections import Counter


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1] if len(data) > 1 else ""

    target = Counter(s)
    limit = 10 ** n

    count = 0
    k = 0
    while k * k < limit:
        v = k * k
        padded = str(v).zfill(n)
        if Counter(padded) == target:
            count += 1
        k += 1

    print(count)


if __name__ == "__main__":
    main()

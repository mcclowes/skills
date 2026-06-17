import sys
from collections import Counter


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1]
    target = Counter(s)

    count = 0
    limit = 10 ** n
    k = 0
    while k * k < limit:
        sq = k * k
        digits = str(sq).zfill(n)
        if len(digits) == n and Counter(digits) == target:
            count += 1
        k += 1

    print(count)


main()

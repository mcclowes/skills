import sys
from collections import Counter


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1] if len(data) > 1 else ""

    target = Counter(s)
    limit = 10 ** n  # numbers strictly less than 10^n have at most n digits

    count = 0
    k = 0
    while k * k < limit:
        sq = k * k
        digits = str(sq).zfill(n)
        # str(sq) never has more than n digits since sq < 10^n; pad to n with leading zeros
        if Counter(digits) == target:
            count += 1
        k += 1
    print(count)


if __name__ == "__main__":
    main()

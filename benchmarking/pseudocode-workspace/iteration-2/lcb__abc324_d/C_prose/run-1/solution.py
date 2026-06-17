import sys
from math import isqrt


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1] if len(data) > 1 else ""

    target = [0] * 10
    for ch in s:
        target[ord(ch) - 48] += 1

    upper = 10 ** n - 1
    limit = isqrt(upper)

    answer = 0
    for k in range(limit + 1):
        x = k * k
        counts = [0] * 10
        t = x
        for _ in range(n):
            counts[t % 10] += 1
            t //= 10
        # t must be 0 since x < 10^n
        if counts == target:
            answer += 1

    print(answer)


if __name__ == "__main__":
    main()

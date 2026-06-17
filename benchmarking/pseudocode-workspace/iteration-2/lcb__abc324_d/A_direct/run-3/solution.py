import sys
from itertools import permutations
from math import isqrt


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1] if len(data) > 1 else ""

    seen = set()
    for perm in permutations(s):
        val = int("".join(perm))
        seen.add(val)

    count = 0
    for v in seen:
        r = isqrt(v)
        if r * r == v:
            count += 1

    print(count)


if __name__ == "__main__":
    main()

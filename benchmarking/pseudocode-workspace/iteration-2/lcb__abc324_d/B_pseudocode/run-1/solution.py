import sys


def main() -> None:
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1] if len(data) > 1 else ""

    target = [0] * 10
    for ch in s:
        target[ord(ch) - 48] += 1

    limit = 10 ** n  # exclusive upper bound on reachable value
    answer = 0
    k = 0
    while k * k < limit:
        v = k * k
        vc = [0] * 10
        if v == 0:
            total_digits = 1
            vc[0] = 1
        else:
            x = v
            total_digits = 0
            while x > 0:
                vc[x % 10] += 1
                x //= 10
                total_digits += 1
        if total_digits <= n:
            vc[0] += n - total_digits  # pad leading zeros to length n
            if vc == target:
                answer += 1
        k += 1

    print(answer)


if __name__ == "__main__":
    main()

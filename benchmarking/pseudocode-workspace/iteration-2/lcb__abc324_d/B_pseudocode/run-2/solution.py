import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1] if len(data) > 1 else ""

    target = [0] * 10
    for ch in s:
        target[ord(ch) - ord('0')] += 1

    limit = 10 ** n
    answer = 0
    k = 0
    while k * k < limit:
        v = k * k
        cnt = [0] * 10
        temp = v
        for _ in range(n):
            cnt[temp % 10] += 1
            temp //= 10
        if cnt == target:
            answer += 1
        k += 1

    print(answer)


if __name__ == "__main__":
    main()

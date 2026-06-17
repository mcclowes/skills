import sys


def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    s = data[1] if len(data) > 1 else ""

    target = [0] * 10
    for ch in s:
        target[ord(ch) - ord('0')] += 1

    max_val = 10 ** n
    count = 0
    i = 0
    while i * i < max_val:
        sq = i * i
        dcnt = [0] * 10
        temp = sq
        for _ in range(n):
            dcnt[temp % 10] += 1
            temp //= 10
        if dcnt == target:
            count += 1
        i += 1

    print(count)


if __name__ == "__main__":
    main()

import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    counts = {}
    for _ in range(n):
        s = int(data[idx]); c = int(data[idx + 1])
        idx += 2
        counts[s] = counts.get(s, 0) + c

    sizes = sorted(counts.keys())
    answer = 0
    i = 0
    while i < len(sizes):
        s = sizes[i]
        c = counts[s]
        # leftover slimes that cannot be paired
        leftover = c % 2
        answer += leftover
        carry = c // 2
        if carry > 0:
            ns = s * 2
            if ns in counts:
                counts[ns] += carry
            else:
                counts[ns] = carry
                # insert ns into sizes keeping sorted order via binary search
                import bisect
                pos = bisect.bisect_right(sizes, ns)
                sizes.insert(pos, ns)
        i += 1

    print(answer)


if __name__ == "__main__":
    main()

import sys
from heapq import heappush, heappop


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    counts = {}
    sizes = []
    for _ in range(n):
        s = int(data[idx]); c = int(data[idx + 1]); idx += 2
        counts[s] = c
        heappush(sizes, s)

    total = 0
    # Process sizes in increasing order; carry pairs up to 2*size.
    while sizes:
        s = heappop(sizes)
        if s not in counts:
            continue
        c = counts.pop(s)
        carry = c // 2
        rem = c % 2
        total += rem
        if carry > 0:
            ns = 2 * s
            if ns in counts:
                counts[ns] += carry
            else:
                counts[ns] = carry
                heappush(sizes, ns)

    print(total)


main()

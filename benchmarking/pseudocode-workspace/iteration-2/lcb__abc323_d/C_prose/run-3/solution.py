import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    counts = {}
    heap = []
    for _ in range(n):
        s = int(data[idx]); idx += 1
        c = int(data[idx]); idx += 1
        if s in counts:
            counts[s] += c
        else:
            counts[s] = c
            heapq.heappush(heap, s)

    ans = 0
    while heap:
        size = heapq.heappop(heap)
        c = counts.pop(size, 0)
        if c == 0:
            continue
        pairs = c // 2
        leftover = c % 2
        ans += leftover
        if pairs > 0:
            up = size * 2
            if up in counts:
                counts[up] += pairs
            else:
                counts[up] = pairs
                heapq.heappush(heap, up)

    print(ans)


if __name__ == "__main__":
    main()

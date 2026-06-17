import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    counts = {}
    heap = []
    for _ in range(n):
        s = int(data[idx]); c = int(data[idx + 1]); idx += 2
        counts[s] = counts.get(s, 0) + c
        heapq.heappush(heap, s)

    answer = 0
    seen = set()
    while heap:
        size = heapq.heappop(heap)
        if size in seen:
            continue
        seen.add(size)
        c = counts[size]
        pairs = c // 2
        leftover = c % 2
        answer += leftover
        if pairs > 0:
            nb = 2 * size
            if nb not in counts:
                counts[nb] = 0
                heapq.heappush(heap, nb)
            counts[nb] += pairs

    sys.stdout.write(str(answer) + "\n")


if __name__ == "__main__":
    main()

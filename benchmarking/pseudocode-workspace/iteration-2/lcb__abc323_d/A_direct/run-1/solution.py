import sys


def main():
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    counts = {}
    for _ in range(n):
        s = int(data[idx]); c = int(data[idx + 1]); idx += 2
        counts[s] = counts.get(s, 0) + c

    # Process sizes in increasing order; carrying merges pairs into 2X.
    sizes = sorted(counts.keys())
    # Use a heap-like ordered processing. Since carries only go upward (to larger
    # sizes that are powers-of-two multiples), process with a pointer over a
    # dynamically growing sorted structure.
    import heapq
    heap = sizes[:]
    heapq.heapify(heap)
    seen = set(sizes)

    answer = 0
    while heap:
        x = heapq.heappop(heap)
        c = counts.get(x, 0)
        if c == 0:
            continue
        pairs = c // 2
        rem = c % 2
        answer += rem
        if pairs > 0:
            nx = x * 2
            if nx not in counts:
                counts[nx] = 0
            counts[nx] += pairs
            if nx not in seen:
                seen.add(nx)
                heapq.heappush(heap, nx)
        counts[x] = 0

    print(answer)


if __name__ == "__main__":
    main()

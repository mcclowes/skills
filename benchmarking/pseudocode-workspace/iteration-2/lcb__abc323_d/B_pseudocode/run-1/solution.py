import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    count = {}
    heap = []
    for _ in range(n):
        s = int(data[idx]); idx += 1
        c = int(data[idx]); idx += 1
        if s in count:
            count[s] += c
        else:
            count[s] = c
            heapq.heappush(heap, s)

    ans = 0
    while heap:
        x = heapq.heappop(heap)
        if x not in count:
            continue
        c = count.pop(x)
        pairs = c // 2
        leftover = c % 2
        ans += leftover
        if pairs > 0:
            y = 2 * x
            if y in count:
                count[y] += pairs
            else:
                count[y] = pairs
                heapq.heappush(heap, y)

    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()

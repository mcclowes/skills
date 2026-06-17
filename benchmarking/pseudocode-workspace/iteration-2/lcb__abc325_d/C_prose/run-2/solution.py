import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    products = []  # (L, R)
    for _ in range(n):
        t = int(data[idx]); d = int(data[idx + 1]); idx += 2
        products.append((t, t + d))

    # Sort by entry time (left endpoint)
    products.sort(key=lambda p: p[0])

    heap = []  # min-heap of deadlines R for currently available products
    i = 0
    count = 0
    cur = products[0][0]  # earliest entry time

    while i < n or heap:
        # Add all products that have entered by time cur
        while i < n and products[i][0] <= cur:
            heapq.heappush(heap, products[i][1])
            i += 1

        # Drop products that have already expired (R < cur)
        while heap and heap[0] < cur:
            heapq.heappop(heap)

        if heap:
            # Print on the most urgent available product
            heapq.heappop(heap)
            count += 1
            cur += 1
        elif i < n:
            # Nothing available now; jump to next entry time
            cur = products[i][0]
        else:
            break

    print(count)


if __name__ == "__main__":
    main()

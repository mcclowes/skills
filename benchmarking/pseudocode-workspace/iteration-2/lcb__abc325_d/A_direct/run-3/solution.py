import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    products = []
    for _ in range(n):
        t = int(data[idx]); idx += 1
        d = int(data[idx]); idx += 1
        products.append((t, t + d))
    # Sort by start time
    products.sort()

    # Sweep over time. Maintain a min-heap of deadlines (end times) of
    # currently available products. At each integer time step, print on the
    # product with the earliest deadline.
    heap = []
    count = 0
    i = 0
    cur = 0
    while i < n or heap:
        if not heap:
            # jump time to next product's start
            cur = products[i][0]
        # add all products that have started by time cur
        while i < n and products[i][0] <= cur:
            heapq.heappush(heap, products[i][1])
            i += 1
        # discard products whose deadline has passed
        while heap and heap[0] < cur:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            count += 1
            cur += 1
        elif i < n:
            cur = products[i][0]

    print(count)


if __name__ == "__main__":
    main()

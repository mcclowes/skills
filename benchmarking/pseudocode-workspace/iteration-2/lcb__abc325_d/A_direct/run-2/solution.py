import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    products = []
    for _ in range(n):
        t = int(data[idx]); d = int(data[idx + 1]); idx += 2
        products.append((t, t + d))

    # Sort by start time
    products.sort()

    # Sweep over candidate print times. At each integer time, among products
    # currently in range, print on the one with the smallest right endpoint.
    heap = []  # min-heap of right endpoints of available products
    count = 0
    i = 0
    time = None
    while i < n or heap:
        if not heap:
            # Jump to the next product's start time
            time = products[i][0]
        # Add all products that have started by current time
        while i < n and products[i][0] <= time:
            heapq.heappush(heap, products[i][1])
            i += 1
        # Discard products that have already expired (right endpoint < time)
        while heap and heap[0] < time:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            count += 1
            time += 1
        # else loop continues; will jump to next start

    print(count)


main()

import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    products = []
    for _ in range(n):
        t = int(data[idx]); d = int(data[idx + 1]); idx += 2
        products.append((t, t + d))  # (left, right) inclusive

    # Sort by left endpoint ascending.
    products.sort()

    heap = []  # min-heap of right endpoints of available, unassigned products
    answer = 0
    i = 0  # pointer into sorted products
    time = None

    while i < n or heap:
        if not heap:
            # Jump to the next product's left endpoint.
            time = products[i][0]
        # Add all products available at the current time.
        while i < n and products[i][0] <= time:
            heapq.heappush(heap, products[i][1])
            i += 1
        # Drop products whose deadline already passed.
        while heap and heap[0] < time:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            answer += 1
            time += 1
        # If heap emptied out by drops with no assignment, loop will jump time.

    print(answer)


if __name__ == "__main__":
    main()

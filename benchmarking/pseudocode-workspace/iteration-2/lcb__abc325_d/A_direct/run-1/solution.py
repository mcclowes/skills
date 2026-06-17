import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    intervals = []
    for _ in range(n):
        t = int(data[idx]); idx += 1
        d = int(data[idx]); idx += 1
        intervals.append((t, t + d))

    # Sort products by start time.
    intervals.sort()

    # Sweep over candidate print times. At each time, among products currently
    # available, prefer printing on the one with the earliest leave time.
    heap = []  # min-heap of leave times for available products
    count = 0
    cur = 0  # next time we are allowed to print
    i = 0
    while i < n or heap:
        if not heap:
            # Jump to the next product's start time.
            cur = intervals[i][0]
        # Add all products that have entered by time `cur`.
        while i < n and intervals[i][0] <= cur:
            heapq.heappush(heap, intervals[i][1])
            i += 1
        # Discard products that have already left.
        while heap and heap[0] < cur:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            count += 1
            cur += 1
        # If heap emptied due to expiry, loop will jump to next start.

    print(count)


if __name__ == "__main__":
    main()

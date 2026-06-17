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
        # available during [t, t + d]
        products.append((t, t + d))

    # sort by left endpoint (start time)
    products.sort()

    heap = []  # min-heap of deadlines (right endpoints) of started products
    i = 0
    count = 0
    t = 0  # current candidate print time

    while i < n or heap:
        if not heap:
            # jump to the next product's start time
            t = products[i][0]
        # push all products that have started by time t
        while i < n and products[i][0] <= t:
            heapq.heappush(heap, products[i][1])
            i += 1
        # discard expired products (deadline before current time)
        while heap and heap[0] < t:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            count += 1
            t += 1
        # if heap emptied by discards, loop will jump to next start

    sys.stdout.write(str(count) + "\n")


if __name__ == "__main__":
    main()

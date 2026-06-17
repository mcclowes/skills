import sys
import heapq


def main() -> None:
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    products = []
    for _ in range(n):
        t = int(data[idx]); idx += 1
        d = int(data[idx]); idx += 1
        L = t
        R = t + d
        products.append((L, R))

    products.sort()  # by L ascending, then R

    heap = []  # min-heap of deadlines R for released, unprinted products
    i = 0
    count = 0
    t = 0

    while i < n or heap:
        if not heap:
            # no released product available; jump to next release time
            t = products[i][0]
        # release all products with L <= t
        while i < n and products[i][0] <= t:
            heapq.heappush(heap, products[i][1])
            i += 1
        # discard products whose deadline has already passed
        while heap and heap[0] < t:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)  # print earliest-deadline product at time t
            count += 1
            t += 1

    sys.stdout.write(str(count) + "\n")


if __name__ == "__main__":
    main()

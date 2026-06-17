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
        products.append((t, t + d))  # (L, R)

    # sort by start time ascending
    products.sort(key=lambda p: p[0])

    heap = []  # min-heap of R (deadline) for active products
    i = 0
    printed = 0
    cur = 0

    while i < n or heap:
        if not heap:
            # jump to the start of the next available product
            cur = products[i][0]
        # add all products that have started by cur
        while i < n and products[i][0] <= cur:
            heapq.heappush(heap, products[i][1])
            i += 1
        # discard expired products
        while heap and heap[0] < cur:
            heapq.heappop(heap)
        if not heap:
            continue
        # print on the earliest-deadline available product
        heapq.heappop(heap)
        printed += 1
        cur += 1

    sys.stdout.write(str(printed) + "\n")


if __name__ == "__main__":
    main()

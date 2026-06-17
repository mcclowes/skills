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
        L = t
        R = t + d
        products.append((L, R))

    products.sort(key=lambda p: p[0])

    pq = []  # min-heap of deadlines R
    count = 0
    i = 0
    t = 0

    while i < n or pq:
        if not pq:
            # jump time forward to next product's release
            t = products[i][0]
        # bring in all products whose L <= t
        while i < n and products[i][0] <= t:
            heapq.heappush(pq, products[i][1])
            i += 1
        # assign current slot to candidate with smallest deadline
        R_min = heapq.heappop(pq)
        if R_min >= t:
            count += 1
            t += 1
        # else: expired, discard, do not advance t

    print(count)


if __name__ == "__main__":
    main()

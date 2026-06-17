import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    m = int(data[idx]); idx += 1

    totals = [0] * n

    # available: min-heap of person indices currently in the row
    available = list(range(n))
    heapq.heapify(available)

    # returning: min-heap of (return_time, person_index)
    returning = []

    for _ in range(m):
        t = int(data[idx]); idx += 1
        w = int(data[idx]); idx += 1
        s = int(data[idx]); idx += 1

        # process all returns that happen at or before time t
        while returning and returning[0][0] <= t:
            _, p = heapq.heappop(returning)
            heapq.heappush(available, p)

        if available:
            p = heapq.heappop(available)
            totals[p] += w
            heapq.heappush(returning, (t + s, p))

    out = "\n".join(map(str, totals))
    sys.stdout.write(out + "\n")


main()

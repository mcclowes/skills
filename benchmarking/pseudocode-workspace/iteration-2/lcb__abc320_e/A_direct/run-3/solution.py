import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    M = int(data[idx]); idx += 1

    totals = [0] * (N + 1)

    # available: min-heap of person indices currently in row
    available = list(range(1, N + 1))
    heapq.heapify(available)

    # busy: min-heap of (return_time, person) for people out of the row
    busy = []

    for _ in range(M):
        T = int(data[idx]); idx += 1
        W = int(data[idx]); idx += 1
        S = int(data[idx]); idx += 1

        # return anyone whose return time <= T
        while busy and busy[0][0] <= T:
            _, person = heapq.heappop(busy)
            heapq.heappush(available, person)

        if available:
            front = heapq.heappop(available)
            totals[front] += W
            heapq.heappush(busy, (T + S, front))

    out = []
    for i in range(1, N + 1):
        out.append(str(totals[i]))
    sys.stdout.write("\n".join(out) + "\n")


main()

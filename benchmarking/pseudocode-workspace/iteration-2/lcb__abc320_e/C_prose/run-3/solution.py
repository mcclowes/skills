import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    m = int(data[idx]); idx += 1

    total = [0] * n
    available = list(range(n))
    heapq.heapify(available)
    returning = []  # (return_time, person_index)

    for _ in range(m):
        t = int(data[idx]); idx += 1
        w = int(data[idx]); idx += 1
        s = int(data[idx]); idx += 1

        # Reinsert people who return at or before this time.
        while returning and returning[0][0] <= t:
            _, p = heapq.heappop(returning)
            heapq.heappush(available, p)

        if available:
            p = heapq.heappop(available)
            total[p] += w
            heapq.heappush(returning, (t + s, p))

    sys.stdout.write("\n".join(map(str, total)) + "\n")


if __name__ == "__main__":
    main()

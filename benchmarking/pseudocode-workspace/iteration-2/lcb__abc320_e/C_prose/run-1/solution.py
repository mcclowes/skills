import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    m = int(data[idx]); idx += 1

    result = [0] * (n + 1)

    # Available people in the row, keyed by index (front = smallest index).
    available = list(range(1, n + 1))
    heapq.heapify(available)

    # People who have stepped out: (return_time, person_index).
    returning = []

    for _ in range(m):
        t = int(data[idx]); idx += 1
        w = int(data[idx]); idx += 1
        s = int(data[idx]); idx += 1

        # Bring back everyone whose return time has arrived (<= t).
        while returning and returning[0][0] <= t:
            _, p = heapq.heappop(returning)
            heapq.heappush(available, p)

        if available:
            p = heapq.heappop(available)
            result[p] += w
            heapq.heappush(returning, (t + s, p))
        # else: no one in the row, noodles are lost.

    out = "\n".join(str(result[i]) for i in range(1, n + 1))
    sys.stdout.write(out + "\n")


if __name__ == "__main__":
    main()

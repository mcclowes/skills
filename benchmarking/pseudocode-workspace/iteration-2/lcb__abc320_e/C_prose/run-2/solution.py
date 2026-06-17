import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    m = int(data[idx]); idx += 1

    total = [0] * (n + 1)

    available = list(range(1, n + 1))
    heapq.heapify(available)
    returning = []  # (return_time, person_index)

    for _ in range(m):
        t = int(data[idx]); idx += 1
        w = int(data[idx]); idx += 1
        s = int(data[idx]); idx += 1

        while returning and returning[0][0] <= t:
            _, p = heapq.heappop(returning)
            heapq.heappush(available, p)

        if available:
            p = heapq.heappop(available)
            total[p] += w
            heapq.heappush(returning, (t + s, p))

    out = "\n".join(str(total[i]) for i in range(1, n + 1))
    sys.stdout.write(out + "\n")


if __name__ == "__main__":
    main()

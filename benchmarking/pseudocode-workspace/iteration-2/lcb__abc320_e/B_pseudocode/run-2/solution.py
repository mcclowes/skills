import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    m = int(data[idx]); idx += 1

    total = [0] * (n + 1)
    available = list(range(1, n + 1))  # already a valid min-heap (sorted ids)
    returning = []  # (return_time, person_id)

    for _ in range(m):
        t = int(data[idx]); idx += 1
        w = int(data[idx]); idx += 1
        s = int(data[idx]); idx += 1

        # People returning at or before t are present
        while returning and returning[0][0] <= t:
            _, pid = heapq.heappop(returning)
            heapq.heappush(available, pid)

        if available:
            pid = heapq.heappop(available)
            total[pid] += w
            heapq.heappush(returning, (t + s, pid))

    out = "\n".join(str(total[i]) for i in range(1, n + 1))
    sys.stdout.write(out + "\n")


if __name__ == "__main__":
    main()

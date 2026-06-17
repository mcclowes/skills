import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    count = {}
    for _ in range(n):
        s = int(data[idx]); c = int(data[idx + 1]); idx += 2
        count[s] = count.get(s, 0) + c

    heap = list(count.keys())
    heapq.heapify(heap)
    processed = set()
    answer = 0

    while heap:
        s = heapq.heappop(heap)
        if s in processed:
            continue
        processed.add(s)
        c = count[s]
        answer += c & 1
        carry = c >> 1
        if carry:
            t = 2 * s
            if t not in count:
                heapq.heappush(heap, t)
            count[t] = count.get(t, 0) + carry

    print(answer)


if __name__ == "__main__":
    main()

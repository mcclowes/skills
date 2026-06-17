import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    cnt = {}
    for _ in range(n):
        s = int(data[idx]); c = int(data[idx + 1]); idx += 2
        cnt[s] = cnt.get(s, 0) + c

    heap = list(cnt.keys())
    heapq.heapify(heap)

    answer = 0
    while heap:
        x = heapq.heappop(heap)
        c = cnt.get(x, 0)
        if c == 0:
            continue
        cnt[x] = 0
        leftover = c % 2
        carry = c // 2
        answer += leftover
        if carry > 0:
            nx = 2 * x
            if cnt.get(nx, 0) == 0:
                heapq.heappush(heap, nx)
            cnt[nx] = cnt.get(nx, 0) + carry

    print(answer)


if __name__ == "__main__":
    main()

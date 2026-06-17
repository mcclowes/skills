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
    in_heap = set(heap)

    answer = 0
    while heap:
        x = heapq.heappop(heap)
        in_heap.discard(x)
        c = cnt[x]
        answer += c % 2
        carry = c // 2
        if carry > 0:
            nx = x * 2
            if nx in cnt:
                cnt[nx] += carry
            else:
                cnt[nx] = carry
            if nx not in in_heap:
                heapq.heappush(heap, nx)
                in_heap.add(nx)

    print(answer)


if __name__ == "__main__":
    main()

import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    A = int(data[idx]); idx += 1
    B = int(data[idx]); idx += 1
    C = int(data[idx]); idx += 1

    D = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            D[i][j] = int(data[idx]); idx += 1

    # State: node index in [0, 2N).
    # 0..N-1   -> car phase at city
    # N..2N-1  -> train phase at city
    INF = float('inf')
    dist = [INF] * (2 * N)
    dist[0] = 0
    pq = [(0, 0)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u < N:
            # car phase at city u
            city = u
            # car edges
            for v in range(N):
                if v == city:
                    continue
                nd = d + D[city][v] * A
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
            # switch to train (free)
            t = city + N
            if d < dist[t]:
                dist[t] = d
                heapq.heappush(pq, (d, t))
        else:
            # train phase at city u-N
            city = u - N
            for v in range(N):
                if v == city:
                    continue
                nd = d + D[city][v] * B + C
                tv = v + N
                if nd < dist[tv]:
                    dist[tv] = nd
                    heapq.heappush(pq, (nd, tv))

    ans = min(dist[N - 1], dist[2 * N - 1])
    print(ans)


main()

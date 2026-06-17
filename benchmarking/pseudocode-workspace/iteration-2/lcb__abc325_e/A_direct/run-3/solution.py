import sys
import heapq


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    A = int(data[idx]); idx += 1
    B = int(data[idx]); idx += 1
    C = int(data[idx]); idx += 1
    D = []
    for i in range(N):
        row = [int(data[idx + j]) for j in range(N)]
        idx += N
        D.append(row)

    INF = float('inf')
    # state 0 = currently using car (can switch to train), state 1 = using train
    # dist[node][state]
    dist = [[INF, INF] for _ in range(N)]
    dist[0][0] = 0
    # priority queue: (time, node, state)
    pq = [(0, 0, 0)]
    while pq:
        t, u, s = heapq.heappop(pq)
        if t > dist[u][s]:
            continue
        for v in range(N):
            if v == u:
                continue
            if s == 0:
                # can travel by car (stay state 0)
                nt = t + D[u][v] * A
                if nt < dist[v][0]:
                    dist[v][0] = nt
                    heapq.heappush(pq, (nt, v, 0))
                # or switch to train (state 1)
                nt2 = t + D[u][v] * B + C
                if nt2 < dist[v][1]:
                    dist[v][1] = nt2
                    heapq.heappush(pq, (nt2, v, 1))
            else:
                # train only
                nt = t + D[u][v] * B + C
                if nt < dist[v][1]:
                    dist[v][1] = nt
                    heapq.heappush(pq, (nt, v, 1))

    print(min(dist[N - 1][0], dist[N - 1][1]))


if __name__ == "__main__":
    main()

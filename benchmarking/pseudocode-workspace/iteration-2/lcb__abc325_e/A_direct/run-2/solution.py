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
    # State: (node, mode) where mode 0 = car, mode 1 = train
    # Start in car mode at node 0.
    dist = [[INF, INF] for _ in range(N)]
    dist[0][0] = 0
    dist[0][1] = 0  # can switch to train at city 1 for free

    pq = [(0, 0, 0)]  # (time, node, mode)

    while pq:
        t, u, mode = heapq.heappop(pq)
        if t > dist[u][mode]:
            continue
        if mode == 0:
            # car: can switch to train at this city for free
            if t < dist[u][1]:
                dist[u][1] = t
                heapq.heappush(pq, (t, u, 1))
            # move by car
            for v in range(N):
                if v == u:
                    continue
                nt = t + D[u][v] * A
                if nt < dist[v][0]:
                    dist[v][0] = nt
                    heapq.heappush(pq, (nt, v, 0))
        else:
            # train: move by train only
            for v in range(N):
                if v == u:
                    continue
                nt = t + D[u][v] * B + C
                if nt < dist[v][1]:
                    dist[v][1] = nt
                    heapq.heappush(pq, (nt, v, 1))

    print(min(dist[N - 1][0], dist[N - 1][1]))


if __name__ == "__main__":
    main()

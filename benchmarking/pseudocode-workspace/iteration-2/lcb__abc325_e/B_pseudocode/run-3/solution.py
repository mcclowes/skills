import sys


def dijkstra_dense(n, dist, edge_cost):
    # dist: initial distances (mutated in place); edge_cost(u, v) -> weight
    INF = float('inf')
    visited = [False] * n
    for _ in range(n):
        u = -1
        best = INF
        for i in range(n):
            if not visited[i] and dist[i] < best:
                best = dist[i]
                u = i
        if u == -1:
            break
        visited[u] = True
        du = dist[u]
        for v in range(n):
            if visited[v]:
                continue
            nd = du + edge_cost(u, v)
            if nd < dist[v]:
                dist[v] = nd
    return dist


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    N = int(data[idx]); idx += 1
    A = int(data[idx]); idx += 1
    B = int(data[idx]); idx += 1
    C = int(data[idx]); idx += 1
    D = [[0] * N for _ in range(N)]
    for i in range(N):
        row = D[i]
        for j in range(N):
            row[j] = int(data[idx]); idx += 1

    INF = float('inf')

    # Car layer Dijkstra from city 0.
    dist_car = [INF] * N
    dist_car[0] = 0
    dijkstra_dense(N, dist_car, lambda u, v: D[u][v] * A)

    # Train layer seeded by free switch at every city.
    dist_train = dist_car[:]  # arrive by car, board train for free
    dijkstra_dense(N, dist_train, lambda u, v: D[u][v] * B + C)

    ans = min(dist_car[N - 1], dist_train[N - 1])
    print(int(ans))


if __name__ == "__main__":
    main()

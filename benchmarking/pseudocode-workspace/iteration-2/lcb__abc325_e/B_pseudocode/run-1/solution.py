import sys


def main() -> None:
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    a = int(data[idx]); idx += 1
    b = int(data[idx]); idx += 1
    c = int(data[idx]); idx += 1

    d = [[0] * n for _ in range(n)]
    for i in range(n):
        row = d[i]
        for j in range(n):
            row[j] = int(data[idx]); idx += 1

    INF = float("inf")

    def dijkstra(init, weight):
        # init: list of starting distances per node
        # weight(i, j): edge cost from i to j
        dist = list(init)
        visited = [False] * n
        for _ in range(n):
            u = -1
            best = INF
            for v in range(n):
                if not visited[v] and dist[v] < best:
                    best = dist[v]
                    u = v
            if u == -1:
                break
            visited[u] = True
            du = dist[u]
            for v in range(n):
                if not visited[v]:
                    nd = du + weight(u, v)
                    if nd < dist[v]:
                        dist[v] = nd
        return dist

    # Phase 1: car only from city 0 (1-indexed city 1)
    car_init = [INF] * n
    car_init[0] = 0
    dist_car = dijkstra(car_init, lambda i, j: d[i][j] * a)

    # Phase 2: train phase; can switch (free) at any city, starting from dist_car
    train_init = list(dist_car)
    dist_train = dijkstra(train_init, lambda i, j: d[i][j] * b + c)

    print(dist_train[n - 1])


if __name__ == "__main__":
    main()

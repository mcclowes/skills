import sys


def dijkstra_dense(n, weight):
    INF = float("inf")
    dist = [INF] * n
    dist[0] = 0
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
        wu = weight[u]
        for v in range(n):
            if not visited[v]:
                nd = du + wu[v]
                if nd < dist[v]:
                    dist[v] = nd
    return dist


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    a = int(data[idx]); idx += 1
    b = int(data[idx]); idx += 1
    c = int(data[idx]); idx += 1

    d = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            d[i][j] = int(data[idx]); idx += 1

    car_w = [[d[i][j] * a for j in range(n)] for i in range(n)]
    train_w = [[d[i][j] * b + c for j in range(n)] for i in range(n)]

    car_dist = dijkstra_dense(n, car_w)

    # Train distance from city N (index n-1) to every city, via train edges.
    INF = float("inf")
    train_dist = [INF] * n
    train_dist[n - 1] = 0
    visited = [False] * n
    for _ in range(n):
        u = -1
        best = INF
        for v in range(n):
            if not visited[v] and train_dist[v] < best:
                best = train_dist[v]
                u = v
        if u == -1:
            break
        visited[u] = True
        du = train_dist[u]
        wu = train_w[u]
        for v in range(n):
            if not visited[v]:
                nd = du + wu[v]
                if nd < train_dist[v]:
                    train_dist[v] = nd

    ans = min(car_dist[k] + train_dist[k] for k in range(n))
    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()

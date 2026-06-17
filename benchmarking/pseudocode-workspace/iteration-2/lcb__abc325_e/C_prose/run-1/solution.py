import sys


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
    # Nodes: 0..N-1 = car layer, N..2N-1 = train layer.
    M = 2 * N
    dist = [INF] * M
    visited = [False] * M
    start = 0  # city 1 (index 0), car layer
    dist[start] = 0

    for _ in range(M):
        # Find unvisited node with smallest distance.
        u = -1
        best = INF
        for v in range(M):
            if not visited[v] and dist[v] < best:
                best = dist[v]
                u = v
        if u == -1:
            break
        visited[u] = True
        du = dist[u]

        if u < N:
            # Car layer: city u.
            row = D[u]
            for j in range(N):
                if j != u:
                    nd = du + row[j] * A
                    if nd < dist[j]:
                        dist[j] = nd
            # Free switch to train at same city.
            tnode = u + N
            if du < dist[tnode]:
                dist[tnode] = du
        else:
            # Train layer: city u - N.
            city = u - N
            row = D[city]
            for j in range(N):
                if j != city:
                    nd = du + row[j] * B + C
                    nj = j + N
                    if nd < dist[nj]:
                        dist[nj] = nd

    ans = min(dist[N - 1], dist[2 * N - 1])
    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()

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

    # Nodes: 0..N-1 car layer, N..2N-1 train layer.
    V = 2 * N
    INF = float('inf')
    dist = [INF] * V
    visited = [False] * V

    dist[0] = 0  # start at city 1 (index 0) in car layer

    for _ in range(V):
        u = -1
        best = INF
        for k in range(V):
            if not visited[k] and dist[k] < best:
                best = dist[k]
                u = k
        if u == -1:
            break
        visited[u] = True
        du = dist[u]

        if u < N:
            # car layer node u (city u)
            # free switch to train layer
            tnode = u + N
            if du < dist[tnode]:
                dist[tnode] = du
            # car edges to all other cities in car layer
            row = D[u]
            for j in range(N):
                if j == u:
                    continue
                nd = du + row[j] * A
                if nd < dist[j]:
                    dist[j] = nd
        else:
            city = u - N
            row = D[city]
            for j in range(N):
                if j == city:
                    continue
                nd = du + row[j] * B + C
                tj = j + N
                if nd < dist[tj]:
                    dist[tj] = nd

    ans = min(dist[N - 1], dist[2 * N - 1])
    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()

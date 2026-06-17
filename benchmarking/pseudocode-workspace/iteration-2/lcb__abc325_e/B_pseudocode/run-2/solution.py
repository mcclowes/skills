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
    # states: car city c -> c ; train city c -> N + c
    S = 2 * N
    dist = [INF] * S
    visited = [False] * S
    dist[0] = 0  # city 0, car

    for _ in range(S):
        # find unvisited min
        u = -1
        best = INF
        for s in range(S):
            if not visited[s] and dist[s] < best:
                best = dist[s]
                u = s
        if u == -1:
            break
        visited[u] = True
        du = dist[u]

        if u < N:
            city = u
            # free switch to train at same city
            t = N + city
            if not visited[t] and du < dist[t]:
                dist[t] = du
            drow = D[city]
            for j in range(N):
                if j == city:
                    continue
                nc = du + drow[j] * A
                if not visited[j] and nc < dist[j]:
                    dist[j] = nc
        else:
            city = u - N
            drow = D[city]
            for j in range(N):
                if j == city:
                    continue
                nc = du + drow[j] * B + C
                tj = N + j
                if not visited[tj] and nc < dist[tj]:
                    dist[tj] = nc

    ans = min(dist[N - 1], dist[2 * N - 1])
    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()

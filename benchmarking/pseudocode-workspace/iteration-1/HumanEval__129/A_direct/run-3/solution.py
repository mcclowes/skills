def minPath(grid, k):
    n = len(grid)
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 1:
                r, c = i, j
    neighbors = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < n:
            neighbors.append(grid[nr][nc])
    second = min(neighbors)
    return [1 if i % 2 == 0 else second for i in range(k)]

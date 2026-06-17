def minPath(grid, k):
    n = len(grid)
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                row, col = r, c
    neighbors = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < n and 0 <= nc < n:
            neighbors.append(grid[nr][nc])
    second = min(neighbors)
    return [1 if i % 2 == 0 else second for i in range(k)]

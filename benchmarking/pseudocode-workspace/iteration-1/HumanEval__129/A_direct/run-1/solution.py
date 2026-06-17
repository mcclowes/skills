def minPath(grid, k):
    n = len(grid)
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 1:
                r, c = i, j
    best = None
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < n:
            v = grid[nr][nc]
            if best is None or v < best:
                best = v
    result = []
    for step in range(k):
        result.append(1 if step % 2 == 0 else best)
    return result

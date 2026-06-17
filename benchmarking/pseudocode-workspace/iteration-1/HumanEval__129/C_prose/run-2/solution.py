def minPath(grid, k):
    n = len(grid)
    # Locate the cell containing the global minimum value 1.
    r = c = 0
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 1:
                r, c = i, j

    # Smallest edge-adjacent neighbor value.
    m = None
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < n:
            v = grid[nr][nc]
            if m is None or v < m:
                m = v

    # Optimal path oscillates between 1 and the smallest neighbor.
    return [1 if i % 2 == 0 else m for i in range(k)]

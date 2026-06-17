def minPath(grid, k):
    n = len(grid)

    # Locate the cell holding the global minimum value 1.
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                row, col = r, c

    # Find the smallest neighbor value of the cell containing 1.
    m = None
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < n and 0 <= nc < n:
            value = grid[nr][nc]
            if m is None or value < m:
                m = value

    # Oscillate between 1 (even indices) and m (odd indices).
    return [1 if i % 2 == 0 else m for i in range(k)]

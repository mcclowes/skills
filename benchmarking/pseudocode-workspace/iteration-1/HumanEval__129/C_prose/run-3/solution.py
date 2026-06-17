def minPath(grid, k):
    n = len(grid)
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                row, col = r, c
                break

    neighbor_min = None
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < n and 0 <= nc < n:
            value = grid[nr][nc]
            if neighbor_min is None or value < neighbor_min:
                neighbor_min = value

    result = []
    for i in range(k):
        result.append(1 if i % 2 == 0 else neighbor_min)
    return result

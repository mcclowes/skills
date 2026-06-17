def minPath(grid, k):
    n = len(grid)
    for i in range(n):
        for j in range(n):
            if grid[i][j] == 1:
                neighbors = []
                if i > 0:
                    neighbors.append(grid[i - 1][j])
                if i < n - 1:
                    neighbors.append(grid[i + 1][j])
                if j > 0:
                    neighbors.append(grid[i][j - 1])
                if j < n - 1:
                    neighbors.append(grid[i][j + 1])
                m = min(neighbors)
                result = []
                for step in range(k):
                    if step % 2 == 0:
                        result.append(1)
                    else:
                        result.append(m)
                return result

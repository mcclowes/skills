import math


def max_fill(grid, capacity):
    import math
    return sum(math.ceil(sum(row) / capacity) for row in grid)

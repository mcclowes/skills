def get_max_triples(n):
    counts = [0, 0, 0]
    for i in range(1, n + 1):
        counts[(i * i - i + 1) % 3] += 1

    def choose3(m):
        return m * (m - 1) * (m - 2) // 6

    c0, c1, c2 = counts
    return choose3(c0) + choose3(c1) + choose3(c2) + c0 * c1 * c2

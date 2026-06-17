def get_max_triples(n):
    counts = [0, 0, 0]
    for i in range(1, n + 1):
        counts[(i * i - i + 1) % 3] += 1

    def choose3(m):
        return m * (m - 1) * (m - 2) // 6

    return (
        choose3(counts[0])
        + choose3(counts[1])
        + choose3(counts[2])
        + counts[0] * counts[1] * counts[2]
    )

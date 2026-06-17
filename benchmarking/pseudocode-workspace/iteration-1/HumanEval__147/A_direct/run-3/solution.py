from itertools import combinations


def get_max_triples(n):
    a = [i * i - i + 1 for i in range(1, n + 1)]
    return sum(1 for x, y, z in combinations(a, 3) if (x + y + z) % 3 == 0)

def generate_integers(a, b):
    lo, hi = min(a, b), max(a, b)
    return [n for n in range(lo, hi + 1) if n in (2, 4, 6, 8)]

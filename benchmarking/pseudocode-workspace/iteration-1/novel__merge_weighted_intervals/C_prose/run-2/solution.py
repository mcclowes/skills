def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights.

    Each input is a tuple (start, end, weight). Intervals are half-open
    [start, end): touching intervals (one ends exactly where the next begins)
    do NOT overlap. Overlapping intervals merge into one spanning
    [min start, max end) with the SUM of merged weights. Overlap is transitive.

    Returns a list of (start, end, weight) tuples sorted by start ascending.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: (iv[0], iv[1]))

    merged = []
    cur_start, cur_end, cur_weight = ordered[0]

    for start, end, weight in ordered[1:]:
        if start < cur_end:  # strict: touching does not overlap
            cur_end = max(cur_end, end)
            cur_weight += weight
        else:
            merged.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = start, end, weight

    merged.append((cur_start, cur_end, cur_weight))
    return merged

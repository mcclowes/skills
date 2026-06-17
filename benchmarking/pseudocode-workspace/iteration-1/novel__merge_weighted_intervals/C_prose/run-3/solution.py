def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights.

    Intervals are [start, end); they overlap only if they share more than a
    single point (strict overlap). Touching endpoints do not merge. Overlap is
    transitive. Returns merged (start, end, weight) tuples sorted by start.
    """
    ordered = sorted(intervals, key=lambda iv: (iv[0], iv[1]))
    if not ordered:
        return []

    merged = []
    cur_start, cur_end, cur_weight = ordered[0]

    for start, end, weight in ordered[1:]:
        if start < cur_end:  # strict overlap; touching does not merge
            cur_end = max(cur_end, end)
            cur_weight += weight
        else:
            merged.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = start, end, weight

    merged.append((cur_start, cur_end, cur_weight))
    return merged

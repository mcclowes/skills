def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights."""
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = []
    cur_start, cur_end, cur_weight = ordered[0]

    for start, end, weight in ordered[1:]:
        if start < cur_end:  # overlap (touching does not count)
            cur_end = max(cur_end, end)
            cur_weight += weight
        else:
            merged.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = start, end, weight

    merged.append((cur_start, cur_end, cur_weight))
    return merged

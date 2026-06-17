def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights."""
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])

    result = []
    cur_start, cur_end, cur_weight = ordered[0]

    for start, end, weight in ordered[1:]:
        if start < cur_end:  # strict: touching (start == cur_end) does not merge
            cur_end = max(cur_end, end)
            cur_weight += weight
        else:
            result.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = start, end, weight

    result.append((cur_start, cur_end, cur_weight))
    return result

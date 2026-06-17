def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights."""
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])

    cur_start, cur_end, cur_weight = ordered[0]
    result = []

    for s, e, w in ordered[1:]:
        if s < cur_end:  # strict: touching (s == cur_end) does not overlap
            cur_end = max(cur_end, e)
            cur_weight += w
        else:
            result.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = s, e, w

    result.append((cur_start, cur_end, cur_weight))
    return result

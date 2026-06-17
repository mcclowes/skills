def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights."""
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])

    result = []
    cur_start, cur_end, cur_w = ordered[0]
    for s, e, w in ordered[1:]:
        if s < cur_end:  # strict: half-open overlap (touching does not count)
            cur_end = max(cur_end, e)
            cur_w += w
        else:
            result.append((cur_start, cur_end, cur_w))
            cur_start, cur_end, cur_w = s, e, w
    result.append((cur_start, cur_end, cur_w))

    return result

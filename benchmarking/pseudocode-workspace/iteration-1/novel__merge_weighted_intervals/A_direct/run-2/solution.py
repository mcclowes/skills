def merge_weighted_intervals(intervals):
    if not intervals:
        return []

    sorted_intervals = sorted(intervals, key=lambda iv: iv[0])

    merged = []
    cur_start, cur_end, cur_weight = sorted_intervals[0]

    for start, end, weight in sorted_intervals[1:]:
        if start < cur_end:
            cur_end = max(cur_end, end)
            cur_weight += weight
        else:
            merged.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = start, end, weight

    merged.append((cur_start, cur_end, cur_weight))
    return merged

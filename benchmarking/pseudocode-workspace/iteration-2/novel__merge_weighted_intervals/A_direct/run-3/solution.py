def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights."""
    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = []
    for start, end, weight in ordered:
        if merged and start < merged[-1][1]:
            prev_start, prev_end, prev_weight = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end), prev_weight + weight)
        else:
            merged.append((start, end, weight))
    return merged

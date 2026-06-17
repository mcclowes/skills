def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights.

    Each input is a tuple (start, end, weight) with start < end. Intervals are
    half-open [start, end): touching intervals (prev_end == next_start) do not
    overlap. Overlapping intervals merge into one spanning [min start, max end)
    whose weight is the sum of merged weights. Overlap is transitive. Returns
    merged intervals sorted by start ascending.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])

    merged = []
    cur_start, cur_end, cur_weight = ordered[0]

    for start, end, weight in ordered[1:]:
        if start < cur_end:  # strict: touching does not overlap
            if end > cur_end:
                cur_end = end
            cur_weight += weight
        else:
            merged.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = start, end, weight

    merged.append((cur_start, cur_end, cur_weight))
    return merged

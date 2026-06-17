def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights.

    Each input is a tuple (start, end, weight) with start < end and weight a
    number. Intervals are half-open [start, end): two intervals that merely
    touch (one ends exactly where the next begins) do NOT overlap.

    Merge any intervals that overlap (share more than a single point) into one
    interval spanning [min start, max end), whose weight is the SUM of the
    weights of all intervals merged into it. Overlap is transitive.

    Return the merged intervals as a list of (start, end, weight) tuples sorted
    by start ascending. Input is not necessarily sorted.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: (iv[0], iv[1]))

    cur_start, cur_end, cur_weight = ordered[0]
    merged = []

    for start, end, weight in ordered[1:]:
        if start < cur_end:  # overlap (touching, start == cur_end, does not count)
            cur_end = max(cur_end, end)
            cur_weight += weight
        else:
            merged.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = start, end, weight

    merged.append((cur_start, cur_end, cur_weight))
    return merged

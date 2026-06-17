def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights.

    Intervals are half-open [start, end): touching (one ends where the next
    begins) does NOT count as overlap. Overlap is transitive. Returns merged
    (start, end, weight) tuples sorted by start ascending.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])

    merged = []
    cur_start, cur_end, cur_weight = ordered[0]

    for s, e, w in ordered[1:]:
        if s < cur_end:  # strict overlap (touching is not overlap)
            cur_end = max(cur_end, e)
            cur_weight += w
        else:
            merged.append((cur_start, cur_end, cur_weight))
            cur_start, cur_end, cur_weight = s, e, w

    merged.append((cur_start, cur_end, cur_weight))
    return merged

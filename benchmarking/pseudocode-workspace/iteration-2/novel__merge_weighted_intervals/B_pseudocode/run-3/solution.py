def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights.

    Each input is a tuple (start, end, weight) with start < end and weight a
    number. Intervals are half-open [start, end): two intervals that merely
    touch (one ends exactly where the next begins) do NOT overlap.

    Merge any intervals that overlap (share more than a single point) into one
    interval spanning [min start, max end), whose weight is the SUM of the
    weights of all intervals merged into it. Overlap is transitive: if A overlaps
    B and B overlaps C, all three merge even if A and C are disjoint.

    Return the merged intervals as a list of (start, end, weight) tuples sorted
    by start ascending. Input is not necessarily sorted.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda iv: iv[0])
    result = []  # list of mutable [start, end, weight] accumulators

    for start, end, weight in ordered:
        if not result or start >= result[-1][1]:
            # Touching (start == last.end) does not overlap, so start a new run.
            result.append([start, end, weight])
        else:
            # start < last.end => overlaps the current run.
            result[-1][1] = max(result[-1][1], end)  # extend, never shrink
            result[-1][2] = result[-1][2] + weight    # sum weights

    return [(s, e, w) for s, e, w in result]

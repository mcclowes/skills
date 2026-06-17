def merge_weighted_intervals(intervals):
    result = []
    for start, end, weight in sorted(intervals):
        if result and start < result[-1][1]:
            ps, pe, pw = result[-1]
            result[-1] = (ps, max(pe, end), pw + weight)
        else:
            result.append((start, end, weight))
    return result

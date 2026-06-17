import sys
from collections import defaultdict


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = data[1:1 + n]

    # Group positions by value
    positions = defaultdict(list)
    for idx in range(n):
        positions[a[idx]].append(idx)

    ans = 0
    for val, pos in positions.items():
        m = len(pos)
        if m < 2:
            continue
        # For each pair (pos[s], pos[t]) with s < t, number of valid j is
        # (pos[t] - pos[s] - 1) - (number of same-value positions strictly between)
        # The number of same-value positions strictly between pos[s] and pos[t] is (t - s - 1).
        # So valid j count = (pos[t] - pos[s] - 1) - (t - s - 1) = pos[t] - pos[s] - (t - s).
        # Sum over all s < t of (pos[t] - pos[s]) - sum over all s < t of (t - s).
        #
        # Sum of (pos[t] - pos[s]) over s < t:
        #   each pos[r] is added (number of s < r) = r times, subtracted (number of t > r) = (m-1-r) times.
        #   = sum_r pos[r] * (r - (m-1-r)) = sum_r pos[r] * (2r - m + 1)
        # Sum of (t - s) over s < t: same form with index r:
        #   = sum_r r * (2r - m + 1)
        sum_pos = 0
        sum_idx = 0
        for r in range(m):
            coef = 2 * r - m + 1
            sum_pos += pos[r] * coef
            sum_idx += r * coef
        ans += sum_pos - sum_idx

    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()

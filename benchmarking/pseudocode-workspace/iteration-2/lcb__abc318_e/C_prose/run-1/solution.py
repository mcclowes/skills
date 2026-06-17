import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = data[1:1 + n]

    # group positions by value; use q = position - rank_within_value
    # for each value, term per pair (a<b) = q_b - q_a where q_x = pos_x - x
    # accumulate sum over pairs in one pass per value.
    from collections import defaultdict

    # store for each value: count seen so far, prefix sum of q values
    counts = defaultdict(int)   # number of occurrences seen
    qsum = defaultdict(int)     # sum of q values seen

    total = 0
    for pos, v in enumerate(a):
        c = counts[v]          # rank index for this new occurrence
        q = pos - c            # q for this occurrence
        # contribution paired with all previous occurrences of same value
        total += q * c - qsum[v]
        qsum[v] += q
        counts[v] = c + 1

    sys.stdout.write(str(total) + "\n")


if __name__ == "__main__":
    main()

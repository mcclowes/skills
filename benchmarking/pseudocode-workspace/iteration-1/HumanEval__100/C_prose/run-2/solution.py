def make_a_pile(n):
    """
    Given a positive integer n, build a pile of n levels of stones.
    The first level has n stones; each subsequent level adds 2, which
    preserves parity and yields the next odd/even number as required.
    Returns a list where index i holds the stone count for level (i+1).
    """
    return [n + 2 * i for i in range(n)]

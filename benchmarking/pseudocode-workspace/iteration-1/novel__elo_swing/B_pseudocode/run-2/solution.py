from math import log


def elo_swing(rating_a, rating_b, score_a, score_b, k=32):
    """Compute player A's new Elo rating after a match, with a
    margin-of-victory multiplier.

    Standard expected score for A:
        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    Actual result for A:
        win  -> 1.0   (score_a > score_b)
        draw -> 0.5   (score_a == score_b)
        loss -> 0.0   (score_a < score_b)

    Margin multiplier (amplifies decisive results, never below 1):
        margin = abs(score_a - score_b)
        mult   = log(margin + 1) base e, but at least 1.0  ->  max(1.0, ln(margin+1))

    New rating for A:
        rating_a + k * mult * (actual_a - expected_a)

    Return the new rating as a float (do not round). A draw must leave the
    multiplier irrelevant only insofar as the formula dictates — apply it as
    written.
    """
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    if score_a > score_b:
        actual_a = 1.0
    elif score_a == score_b:
        actual_a = 0.5
    else:
        actual_a = 0.0

    margin = abs(score_a - score_b)
    mult = max(1.0, log(margin + 1))

    return rating_a + k * mult * (actual_a - expected_a)

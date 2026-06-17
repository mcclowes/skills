from math import log


def elo_swing(rating_a, rating_b, score_a, score_b, k=32):
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

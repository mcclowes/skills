# Plan: elo_swing

## Input/output contract

The function `elo_swing(rating_a, rating_b, score_a, score_b, k=32)` takes the
current Elo ratings of two players (numeric), the match scores each achieved
(numeric), and an optional sensitivity factor `k` defaulting to 32. It returns
player A's updated Elo rating as a `float`, deliberately unrounded.

## Algorithm steps

1. **Expected score.** Compute A's expected probability of winning using the
   standard logistic Elo formula:
   `expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))`.
   This yields a value in (0, 1); when the ratings are equal it is exactly 0.5.

2. **Actual result.** Compare the two scores. If `score_a > score_b`, A won and
   the actual result is `1.0`. If they are equal, it is a draw worth `0.5`. If
   `score_a < score_b`, A lost and it is `0.0`.

3. **Margin-of-victory multiplier.** Take the absolute score difference
   `margin = abs(score_a - score_b)`. The raw multiplier is `ln(margin + 1)`
   (natural log via `math.log`). Floor it at `1.0` with `max(1.0, ...)` so the
   multiplier never shrinks a rating change below the base amount.

4. **New rating.** Apply `rating_a + k * mult * (actual_a - expected_a)` and
   return it as a float.

## Edge cases

- **Draw:** `margin` is 0, so `ln(1) = 0`, and `max(1.0, 0)` gives `1.0`; the
  multiplier is applied as written (irrelevant in effect since actual equals
  expected only when ratings match, otherwise it scales the small delta by 1).
- **Equal ratings:** expected is exactly 0.5, avoiding any division issues.
- **Large margins:** the log keeps growth gentle, avoiding runaway swings.
- **Integer or float inputs** are both handled; the return is always a float.

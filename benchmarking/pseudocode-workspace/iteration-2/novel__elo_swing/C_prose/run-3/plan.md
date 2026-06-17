# Plan: elo_swing

## Contract
Inputs: `rating_a`, `rating_b` (numeric current Elo ratings for players A and
B), `score_a`, `score_b` (numeric match scores for A and B), and an optional
`k` factor defaulting to 32. Output: a single float, player A's new Elo rating,
returned without rounding.

## Algorithm
1. Compute A's expected score using the standard logistic formula:
   `expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))`. This yields a
   value in (0, 1) representing A's probability-weighted expected result.
2. Determine A's actual result by comparing scores: 1.0 if `score_a > score_b`
   (win), 0.5 if equal (draw), 0.0 if `score_a < score_b` (loss).
3. Compute the margin of victory as `abs(score_a - score_b)` and the multiplier
   as `max(1.0, log(margin + 1))`, using the natural logarithm (base e). The
   `max` clamp guarantees the multiplier is never below 1.0, so small or zero
   margins do not shrink the rating change.
4. Return `rating_a + k * mult * (actual_a - expected_a)`.

## Edge cases
- Draw (`score_a == score_b`): margin is 0, so `log(1) = 0`, and `max(1.0, 0)`
  clamps the multiplier to 1.0. Actual is 0.5; the formula is applied exactly
  as written.
- Equal ratings: expected_a is exactly 0.5, which is fine.
- Large margins amplify the swing via the natural-log multiplier.
- No rounding is applied; the raw float is returned. Scores may be ints or
  floats; arithmetic handles both.

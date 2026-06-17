# Plan: elo_swing

## Contract
`elo_swing(rating_a, rating_b, score_a, score_b, k=32)` returns player A's new Elo
rating as a float. Inputs: `rating_a`, `rating_b` are numeric current ratings;
`score_a`, `score_b` are the numeric match scores for the two players; `k` is the
Elo K-factor (default 32). Output: a single float, not rounded.

## Data
All inputs are numbers (ints or floats). No collections or external state are
involved. We use `math.log` (natural log) for the margin multiplier and the `**`
operator for the expected-score logistic curve.

## Algorithm
1. Expected score for A using the standard Elo logistic:
   `expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))`.
2. Determine the actual result for A from the raw scores:
   - `score_a > score_b` -> `1.0` (win)
   - `score_a == score_b` -> `0.5` (draw)
   - `score_a < score_b` -> `0.0` (loss)
3. Margin of victory: `margin = abs(score_a - score_b)`.
4. Multiplier: `mult = max(1.0, math.log(margin + 1))` (natural log, floored at 1.0).
5. New rating: `rating_a + k * mult * (actual_a - expected_a)`.
6. Return as a float.

## Edge cases
- Draw: margin is 0, so `log(1) = 0`, then `max(1.0, 0) = 1.0`. The multiplier is
  thus exactly 1.0, but it is applied as written per the spec.
- Margin of 1: `log(2) ~= 0.693`, so `max` floors it to 1.0 (multiplier never
  drops below 1).
- Larger margins amplify the swing.
- Equal ratings give `expected_a = 0.5`.
- `argin + 1` is always positive, so `log` is always defined.

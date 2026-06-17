# Plan: elo_swing

## Contract
- Inputs: `rating_a`, `rating_b` (numeric Elo ratings for players A and B), `score_a`, `score_b` (numeric match scores for A and B), and `k` (the K-factor, default 32, controlling rating volatility).
- Output: a single `float` — player A's new Elo rating after the match. The result is intentionally not rounded.

## Data
Everything is scalar numeric. No collections, no I/O. The only library dependency is the natural logarithm, which I'll pull from Python's `math` module.

## Algorithm
1. Compute A's expected score against B using the logistic Elo formula:
   `expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))`. This yields a value in (0, 1) representing A's win probability.
2. Determine A's actual result by comparing scores: `1.0` if `score_a > score_b` (win), `0.5` if equal (draw), `0.0` if `score_a < score_b` (loss).
3. Compute the margin of victory: `margin = abs(score_a - score_b)`.
4. Compute the margin multiplier: `mult = max(1.0, log(margin + 1))`, using natural log. Because `log(margin + 1)` only exceeds 1 once `margin + 1 > e` (margin > ~1.718), the `max(1.0, ...)` floor keeps the multiplier from shrinking the rating change for small margins.
5. Return `rating_a + k * mult * (actual_a - expected_a)`.

## Edge cases
- Draw: `margin == 0`, so `log(1) == 0`, and the floor clamps `mult` to `1.0`; `actual_a - expected_a` then drives the change as the formula dictates.
- Margin of 1: `log(2) ≈ 0.693`, again clamped to `1.0`.
- Equal ratings: expected score is exactly `0.5`.
- The argument to `log` is always `>= 1` since margin is non-negative, so no domain errors arise.
- No rounding is applied, preserving full float precision.

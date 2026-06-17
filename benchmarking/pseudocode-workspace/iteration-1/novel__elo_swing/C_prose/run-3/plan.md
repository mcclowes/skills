# Plan: elo_swing

## Input/output contract

`elo_swing(rating_a, rating_b, score_a, score_b, k=32)` takes player A's and B's
current Elo ratings (numbers), the match scores for each player (numbers, e.g.
goals or points), and an optional development coefficient `k` (default 32). It
returns player A's new Elo rating as a `float`, unrounded.

## Algorithm steps

1. **Expected score.** Compute A's expected result from the standard logistic
   Elo formula: `expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))`.
   This yields a value in (0, 1) representing A's win probability.
2. **Actual result.** Compare the two scores to derive A's actual outcome:
   `1.0` if `score_a > score_b` (win), `0.5` if equal (draw), `0.0` if
   `score_a < score_b` (loss).
3. **Margin multiplier.** Take the absolute score difference,
   `margin = abs(score_a - score_b)`, then compute `ln(margin + 1)` using the
   natural logarithm. Clamp it to a floor of `1.0`:
   `mult = max(1.0, log(margin + 1))`. This amplifies decisive wins while never
   shrinking the swing below the standard amount.
4. **New rating.** Apply the update:
   `rating_a + k * mult * (actual_a - expected_a)`.

## Edge cases

- **Draw:** `margin` is 0, so `log(1) = 0`, and `max(1.0, 0) = 1.0`; the
  multiplier is exactly 1.0, as the spec dictates we apply the formula as
  written.
- **Margin of 0 or 1:** both produce a multiplier of 1.0 (log floor), so small
  margins behave like standard Elo.
- **Negative scores / differences:** `abs` keeps the margin non-negative, so the
  log argument `margin + 1 >= 1` and is always valid (no domain error).
- **No rounding:** the result is returned as a raw float per the contract.

I use `math.log` (natural log) and avoid mutating inputs.

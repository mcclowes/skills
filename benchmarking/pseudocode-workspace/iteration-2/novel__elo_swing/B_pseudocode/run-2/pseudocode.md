# elo_swing — plan

Numerical formula with a couple of subtle spots (margin multiplier floor, draw result). Planning the core.

## Data & invariants
- rating_a, rating_b: floats (Elo ratings).
- score_a, score_b: numbers (match scores). Compared only by sign of difference.
- k: float, default 32.
- Output: float (new rating), unrounded.
- Invariant: mult >= 1.0 always (floor). expected_a in (0,1).

## Control flow
expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

actual_a:
  if score_a > score_b -> 1.0
  elif score_a == score_b -> 0.5
  else -> 0.0

margin = abs(score_a - score_b)
mult = max(1.0, ln(margin + 1))      # natural log

return rating_a + k * mult * (actual_a - expected_a)

## Edge cases
- draw: margin = 0 -> ln(1) = 0 -> mult = max(1.0, 0) = 1.0. Also actual_a - expected_a may be negative; formula applied as written. Fine.
- margin = 1 -> ln(2) ≈ 0.693 -> mult floored to 1.0.
- large margin -> mult > 1 amplifies.
- ln(margin+1) never gets ln(0) since margin >= 0 so arg >= 1.
- equal ratings -> expected_a = 0.5.

## Interface contract
- Pure function, no mutation, returns float, no rounding.

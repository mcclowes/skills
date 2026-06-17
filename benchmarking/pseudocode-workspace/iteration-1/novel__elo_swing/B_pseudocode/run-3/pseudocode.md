# elo_swing plan

Verdict: numerical formula with a clamp and branching — plan the core.

## Data & contract
- Inputs: rating_a, rating_b (numbers), score_a, score_b (numbers), k (default 32).
- Output: new rating for A as a float, NOT rounded.
- Pure function, no mutation, no error handling specified for bad input.

## Control flow
expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

actual_a:
  if score_a > score_b -> 1.0
  elif score_a == score_b -> 0.5
  else -> 0.0

margin = abs(score_a - score_b)
mult = max(1.0, ln(margin + 1))   # natural log, clamped at 1.0

new_rating = rating_a + k * mult * (actual_a - expected_a)
return float(new_rating)

## Edge cases
- draw: margin = 0 -> ln(1) = 0 -> mult = max(1.0, 0) = 1.0; (actual-expected) drives result.
- margin small (1): ln(2) ~ 0.693 < 1 -> clamped to 1.0.
- margin where ln(margin+1) > 1 (margin >= ~1.718, i.e. >=2): mult > 1, amplifies.
- equal ratings: expected_a = 0.5.

## Invariants
- mult >= 1.0 always.
- ln is base e (natural log).

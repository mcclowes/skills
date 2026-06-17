# elo_swing — pseudocode plan

Verdict: numerical formula with a multiplier floor and a draw case — planning first.

## Data & invariants
- Inputs: rating_a, rating_b (numbers), score_a, score_b (numbers), k (default 32).
- expected_a in (0, 1).
- actual_a in {0.0, 0.5, 1.0}.
- mult >= 1.0 always (floor applies; ln(margin+1) can be < 1 for small margins, e.g. margin 0 -> ln(1)=0).
- Output is a float; no rounding.

## Control flow
```
expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

if score_a > score_b:  actual_a = 1.0
elif score_a == score_b: actual_a = 0.5
else: actual_a = 0.0

margin = abs(score_a - score_b)
mult = max(1.0, ln(margin + 1))     # natural log, base e

new_rating = rating_a + k * mult * (actual_a - expected_a)
return new_rating
```

## Edge cases & failure modes
- Draw (score_a == score_b): margin = 0, ln(1) = 0, mult = max(1.0, 0) = 1.0. Formula applied as written.
- Margin 1: ln(2) ≈ 0.693 < 1 -> mult floored to 1.0.
- Margin where ln(margin+1) > 1 (margin >= e-1 ≈ 1.718, i.e. margin >= 2): mult = ln(margin+1).
- Equal ratings: expected_a = 0.5.
- No rounding — return raw float.

## Interface contract
- Pure function. Returns new rating for A as float. No mutation, no exceptions for normal numeric inputs.

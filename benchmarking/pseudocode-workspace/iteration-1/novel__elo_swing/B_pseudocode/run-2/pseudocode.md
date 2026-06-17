# elo_swing — plan

Verdict: numerical formula with a margin multiplier and a max-clamp. Planning the tricky core (multiplier, actual result, clamp) first.

## Data & invariants
- Inputs: rating_a, rating_b (floats), score_a, score_b (numbers), k (float, default 32).
- expected_a ∈ (0,1).
- actual_a ∈ {0.0, 0.5, 1.0}.
- mult ≥ 1.0 always (clamp lower bound).
- Output: float, unrounded.

## Control flow
```
expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

if score_a > score_b: actual_a = 1.0
elif score_a == score_b: actual_a = 0.5
else: actual_a = 0.0

margin = abs(score_a - score_b)
mult = max(1.0, ln(margin + 1))          # natural log, base e

new = rating_a + k * mult * (actual_a - expected_a)
return new   # no rounding
```

## Edge cases
- Draw: margin = 0 → ln(1) = 0 → max(1.0, 0) = 1.0. actual_a - expected_a still nonzero, so rating moves per formula. Apply as written (don't special-case to "no change").
- margin = 1 → ln(2) ≈ 0.693 → clamped up to 1.0.
- margin large → mult = ln(margin+1) > 1, amplifies.
- Equal ratings → expected_a = 0.5.

## Contract
- Pure. Returns float. No rounding. Uses math.log (natural log).

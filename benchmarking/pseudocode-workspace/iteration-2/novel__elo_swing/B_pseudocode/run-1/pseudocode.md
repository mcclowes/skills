# elo_swing — plan

Verdict: numerical formula with a small branch + a clamp. Slightly off = silently wrong. Plan first.

## Data & invariants
- Inputs: rating_a, rating_b (numbers), score_a, score_b (numbers), k (default 32).
- expected_a in (0,1). actual_a in {0.0, 0.5, 1.0}. mult >= 1.0 always.
- Output: float (no rounding).

## Control flow
1. expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
2. actual_a:
   - score_a > score_b -> 1.0
   - score_a == score_b -> 0.5
   - else (score_a < score_b) -> 0.0
3. margin = abs(score_a - score_b)
4. mult = max(1.0, ln(margin + 1))   # natural log, base e
5. return rating_a + k * mult * (actual_a - expected_a)

## Edge cases
- draw: margin = 0 -> ln(1) = 0 -> max(1.0, 0) = 1.0; (actual_a - expected_a) handles direction. OK.
- margin 1 -> ln(2) ~= 0.693 < 1 -> clamped to 1.0. Clamp matters here.
- margin large -> mult > 1, amplifies. OK.
- equal ratings, win: expected_a = 0.5, gain = k*mult*0.5.

## Contract
Pure. Returns float, unrounded. ln via math.log (default base e).

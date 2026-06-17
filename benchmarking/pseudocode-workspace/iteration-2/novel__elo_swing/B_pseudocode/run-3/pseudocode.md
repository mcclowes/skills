# elo_swing — plan

Verdict: numerical formula with branchy actual-score + a log multiplier. Slightly-off is silently wrong. Plan first.

## Data & invariants
- Inputs: rating_a, rating_b (numbers), score_a, score_b (numbers), k (default 32).
- expected_a in (0,1), monotone in rating difference.
- mult >= 1.0 always (max clamp). margin >= 0 so ln(margin+1) >= ln(1)=0; clamp lifts to 1.0.
- Output: float.

## Control flow
1. expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
2. actual_a:
   - score_a > score_b -> 1.0
   - score_a == score_b -> 0.5
   - else -> 0.0
3. margin = abs(score_a - score_b)
4. mult = max(1.0, ln(margin + 1))     # natural log
5. return rating_a + k * mult * (actual_a - expected_a)

## Edge cases
- Draw: margin = 0 -> ln(1)=0 -> mult clamped to 1.0. actual-expected term drives change. Apply as written.
- Small margin (1,2): ln(2)=0.693, ln(3)=1.099 -> clamp matters for margin 1 (0.693 -> 1.0).
- Equal ratings, win: expected 0.5, gain = k*mult*0.5.
- No rounding; return float (ensure float via the arithmetic, k*... is float).

## Contract
- Pure. Returns new rating as float. No mutation, no rounding.

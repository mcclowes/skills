# Plan: elo_swing

## Input/output contract
The function takes five values: `rating_a` and `rating_b` (numeric current Elo
ratings of the two players), `score_a` and `score_b` (the numeric scores each
player achieved in the match, used both to decide the result and to compute the
margin of victory), and an optional `k` factor defaulting to 32. It returns a
single float: player A's new Elo rating, unrounded.

## Algorithm steps
1. Compute A's expected score using the standard logistic formula:
   `expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))`. This yields a
   value in (0, 1) representing A's probability-weighted expectation.
2. Determine A's actual result from the comparison of scores: `1.0` if A scored
   strictly more than B (win), `0.5` if the scores are equal (draw), and `0.0`
   if A scored strictly less (loss).
3. Compute the margin of victory as the absolute difference of the scores:
   `margin = abs(score_a - score_b)`.
4. Compute the multiplier `mult = max(1.0, log(margin + 1))` using the natural
   logarithm. The `+1` keeps the argument >= 1 so the log is non-negative, and
   the `max` floors the multiplier at 1.0 so it never shrinks a swing.
5. Return `rating_a + k * mult * (actual_a - expected_a)`.

## Edge cases
- Draw: `margin == 0` gives `log(1) == 0`, so `mult` floors to `1.0`; the swing
  term is `k * 1.0 * (0.5 - expected_a)`, applied as the spec dictates.
- Small margins (margin of 1) give `log(2) ~= 0.693`, below 1, so the floor of
  1.0 applies. Larger margins push the multiplier above 1.0, amplifying decisive
  results.
- Negative score differences are handled by `abs`, so order of scores does not
  affect the margin magnitude.
- No rounding is performed; the raw float is returned.

## Implementation notes
Only `math.log` is needed (natural log is the default base in Python).

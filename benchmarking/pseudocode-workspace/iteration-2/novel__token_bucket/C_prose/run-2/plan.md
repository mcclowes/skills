# Plan: token_bucket rate limiter

## Input/output contract
- Inputs: `capacity` (number, max bucket level), `refill_per_sec` (number, tokens
  added per second of elapsed time), and `events`, a list of
  `(timestamp_seconds, cost)` tuples given in non-decreasing timestamp order.
- Output: a list of booleans of the same length as `events`, where element `i` is
  `True` if event `i` was allowed and `False` if it was denied.

## State
- `tokens`: current bucket level, a real number. Starts at `capacity` (full).
- `last_ts`: timestamp of the previous event, used to compute elapsed time. There
  is no "previous event" before the first one, so the first event sees zero
  elapsed time (the bucket is already full and no refill is needed).

## Algorithm
For each `(ts, cost)` in `events`, in order:
1. Compute `elapsed = ts - last_ts`. For the first event this is `ts - ts = 0`
   if we initialise `last_ts` from the first timestamp, but to be safe we only
   refill when there is a known previous timestamp.
2. Refill: `tokens = min(capacity, tokens + refill_per_sec * elapsed)`. The `min`
   enforces the upper bound so the level never exceeds `capacity`.
3. Decide: if `tokens >= cost`, append `True` and set `tokens -= cost`;
   otherwise append `False` and leave `tokens` unchanged.
4. Update `last_ts = ts` regardless of allow/deny, since time advances either way.

## Edge cases
- Empty `events`: return `[]`.
- First event: no refill (bucket already full); elapsed effectively 0.
- Repeated timestamps (elapsed 0): no refill between them, which matches the
  example where two events at t=0 both draw from the full bucket.
- `cost == 0`: always allowed (0 <= tokens), subtracting 0 is a no-op.
- Floating-point: tokens stay in `[0, capacity]` because we never add past
  `capacity` and only subtract `cost` when `tokens >= cost`, keeping it >= 0.
- Non-decreasing timestamps mean `elapsed >= 0`, so refill is never negative.

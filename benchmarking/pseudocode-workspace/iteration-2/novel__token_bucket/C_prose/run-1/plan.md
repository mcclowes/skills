# Plan: token_bucket

## Input/output contract
- Inputs: `capacity` (number, max tokens the bucket holds), `refill_per_sec`
  (number, tokens added per second of elapsed time), and `events`, a list of
  `(timestamp_seconds, cost)` tuples sorted in non-decreasing timestamp order.
- Output: a list of booleans, one per event, in the same order. `True` means the
  event was allowed (and its cost deducted); `False` means it was denied (bucket
  untouched).

## Data and state
- `level`: a float tracking current tokens. Starts at `capacity` (bucket full).
- `last_t`: the timestamp of the previous event, used to compute elapsed time.
  Initialised to the first event's timestamp so the first refill is zero.

## Algorithm steps
For each `(t, cost)` event in order:
1. Compute `elapsed = t - last_t`. Because timestamps are non-decreasing,
   elapsed is always >= 0.
2. Refill: `level = min(capacity, level + refill_per_sec * elapsed)`. The `min`
   caps the bucket at capacity so it never overflows.
3. Update `last_t = t`.
4. Decision: if `level >= cost`, allow — append `True` and set
   `level -= cost`. Otherwise deny — append `False`, leaving `level` unchanged.

## Edge cases
- Empty `events` -> return `[]`.
- Multiple events at the same timestamp: elapsed is 0, no refill between them.
- `cost == 0`: always allowed (level >= 0 >= 0), no change. Cost greater than
  capacity is always denied.
- Tokens are real numbers; no rounding is applied, so float arithmetic is used
  directly. Level stays within `[0, capacity]` by construction (refill caps at
  capacity, spending only happens when affordable).

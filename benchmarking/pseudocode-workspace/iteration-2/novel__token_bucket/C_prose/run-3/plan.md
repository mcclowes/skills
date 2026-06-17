# Token bucket rate limiter — plan

## Input/output contract
- `capacity`: a non-negative real number, the maximum tokens the bucket can hold.
- `refill_per_sec`: a non-negative real number, tokens added per second of elapsed time.
- `events`: a list of `(timestamp_seconds, cost)` tuples, ordered by non-decreasing timestamp.
- Output: a list of booleans of the same length as `events`, one per event, `True` if allowed and `False` if denied.

## Algorithm
The bucket starts full at `capacity` tokens. We track the current token level and the timestamp of the previous event. For each event in order:
1. Compute `elapsed = timestamp - last_timestamp`. For the very first event there is no prior reference, so elapsed is zero (the bucket is already full, so refill is moot anyway).
2. Refill: `level = min(capacity, level + refill_per_sec * elapsed)`. The `min` clamps to capacity so we never overflow.
3. Decide: if `level >= cost`, the event is allowed — append `True` and subtract `cost` from `level`. Otherwise it is denied — append `False` and leave `level` unchanged.
4. Update `last_timestamp = timestamp` regardless of allow/deny, so future elapsed values are measured from the most recent event.

## Edge cases
- Empty `events`: return `[]`.
- Zero-cost events: `level >= 0` always holds (level never goes negative), so they are allowed and subtract nothing.
- Multiple events at the same timestamp: elapsed is zero, so no refill happens between them — matches the example where two cost-5 spends drain the bucket.
- `cost > capacity`: can never be satisfied, always denied.
- Tokens are real numbers; no rounding is applied. The `min` clamp keeps level in `[0, capacity]`; level only decreases on allow and only increases via clamped refill, so it stays in range.

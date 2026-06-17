# Plan: token_bucket rate limiter

## Contract
- Inputs:
  - `capacity` (number): max tokens the bucket can hold.
  - `refill_per_sec` (number): tokens added per second of elapsed time.
  - `events` (list of `(timestamp_seconds, cost)` tuples) in non-decreasing
    timestamp order.
- Output: a list of booleans, one per event. `True` = allowed, `False` = denied.

## Data and state
We carry two pieces of state across the loop: `level` (current tokens, a real
number) and `last_ts` (timestamp of the previous event). The bucket starts full,
so `level = capacity`. For the first event there is no prior event; the natural
choice is to seed `last_ts` with the first event's timestamp so the initial
elapsed time is zero (the bucket is already full, so no refill is needed before
the first event anyway).

## Algorithm
For each `(ts, cost)` event in order:
1. Compute `elapsed = ts - last_ts`. Because timestamps are non-decreasing,
   elapsed is never negative.
2. Refill: `level = min(capacity, level + refill_per_sec * elapsed)`. The `min`
   clamps to capacity so tokens never overflow.
3. Update `last_ts = ts` regardless of allow/deny, since refill is purely
   time-based.
4. Decide: if `level >= cost`, append `True` and subtract: `level -= cost`.
   Otherwise append `False` and leave `level` unchanged.

## Edge cases
- Empty `events` -> return `[]`.
- Multiple events at the same timestamp -> elapsed is 0, so no refill between
  them (matches the example).
- `cost` of 0 -> always allowed, subtracts nothing.
- Floating-point drift: clamp on refill keeps `level <= capacity`; subtraction
  only happens when `level >= cost`, keeping `level >= 0`.
- `cost > capacity` -> can never be satisfied -> always denied.

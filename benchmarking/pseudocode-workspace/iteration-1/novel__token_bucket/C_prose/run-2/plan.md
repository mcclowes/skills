# Plan: token_bucket rate limiter

## Input/output contract
- Inputs: `capacity` (number, max tokens the bucket holds), `refill_per_sec` (number, tokens added per second of elapsed time), and `events`, a list of `(timestamp_seconds, cost)` tuples sorted in non-decreasing timestamp order.
- Output: a list of booleans, one per event, `True` if the event was allowed (enough tokens, cost deducted) and `False` if denied (insufficient tokens, bucket left unchanged).

## Data and state
The only mutable state is the current token level (`tokens`, a real number) and the timestamp of the previous event (`last_ts`). The bucket starts full at `capacity`, and `last_ts` is initialised from the first event's timestamp so the first refill contributes zero.

## Algorithm
1. Initialise `tokens = capacity`. Track `last_ts` lazily: for the first event treat elapsed time as zero.
2. For each `(ts, cost)`:
   a. Compute `elapsed = ts - last_ts` (non-negative because timestamps are non-decreasing).
   b. Refill: `tokens = min(capacity, tokens + refill_per_sec * elapsed)`.
   c. Update `last_ts = ts`.
   d. If `tokens >= cost`, append `True` and set `tokens -= cost`; else append `False` and leave `tokens` unchanged.

## Edge cases
- Empty events list -> return `[]`.
- Multiple events at the same timestamp -> elapsed is 0, no refill between them (matches the example where two t=0 events drain the bucket).
- `cost` of 0 -> always allowed (0 >= 0), subtracting 0 is harmless.
- Refill capping ensures `tokens` never exceeds `capacity`; subtraction only happens when `tokens >= cost`, so `tokens` never drops below 0. Level stays in `[0, capacity]`.
- Floating-point comparison: use a direct `>=` per the spec (no rounding). A tiny epsilon could be added but the spec says exact reals, so we keep it exact.

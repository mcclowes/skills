# Plan: token-bucket rate limiter

## Input/output contract

`token_bucket(capacity, refill_per_sec, events)` takes a numeric `capacity` (max
tokens the bucket can hold), a numeric `refill_per_sec` (tokens added per second),
and `events`, a list of `(timestamp_seconds, cost)` tuples sorted in non-decreasing
timestamp order. It returns a list of booleans, one per event, where `True` means
the event was allowed and `False` means it was denied.

## State

The only mutable state is `level`, the current number of tokens in the bucket, a
real number kept within `[0, capacity]`. The bucket starts full, so `level =
capacity`. We also track `last_ts`, the timestamp of the previous processed event,
to compute elapsed time for refills.

## Algorithm

1. Initialize `level = capacity` and `last_ts = None`.
2. For each `(ts, cost)` event:
   - If this is not the first event, compute `elapsed = ts - last_ts` and refill:
     `level = min(capacity, level + refill_per_sec * elapsed)`. The first event has
     no prior reference, so no refill happens before it (the bucket is already full).
   - Update `last_ts = ts` regardless of allow/deny, since time has advanced.
   - If `level >= cost`, append `True` and subtract: `level -= cost`.
   - Otherwise append `False` and leave `level` unchanged.

## Edge cases

- Empty `events` list returns `[]`.
- Duplicate timestamps (`elapsed = 0`) add zero tokens, correctly serializing
  same-instant events (matches the example).
- `cost` of 0 is always allowed and changes nothing.
- A `cost` exceeding `capacity` can never be satisfied, so it is always denied.
- Refill is clamped with `min` so `level` never exceeds `capacity`; subtraction
  only happens when `level >= cost`, so `level` never drops below 0.
- Tokens stay as floats; no rounding is applied.

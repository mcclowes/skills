# token_bucket — plan

Verdict: numerical state machine with an invariant (level in [0, capacity]) and
ordering across events. Plan first.

## Data & invariants
- `level`: real number, current tokens. Invariant: 0 <= level <= capacity, always.
- `last_t`: timestamp of the previous event (for elapsed computation).
- Initial: level = capacity, last_t = timestamp of first event (or undefined until first).
- elapsed = current_t - last_t, always >= 0 (timestamps non-decreasing).

## Control flow
```
level   <- capacity
last_t  <- None
result  <- empty list

for each (t, cost) in events:
    if last_t is not None:
        elapsed <- t - last_t          # >= 0 by precondition
        level   <- min(capacity, level + refill_per_sec * elapsed)
    last_t <- t                        # advance clock every event, allow or deny

    if level >= cost:
        level <- level - cost          # ALLOW
        append True
    else:
        append False                   # DENY, level unchanged

return result
```

## Edge cases & failure modes
- empty events            -> return empty list.
- first event             -> no refill (last_t None), bucket starts full.
- multiple events same t  -> elapsed 0, no refill between them (matches example).
- cost 0                  -> level >= 0 always true -> ALLOW, subtract 0 (no-op).
- cost > capacity         -> can never be satisfied -> always DENY.
- refill caps at capacity -> min() guards upper bound; level never exceeds capacity.
- deny does not consume   -> level untouched, clock still advances.
- floating point          -> level >= cost comparison kept as-is (no rounding per spec).

## Interface contract
- Inputs: capacity (number), refill_per_sec (number), events (list of (t, cost)).
- Output: list[bool], one per event in order.
- Pure: does not mutate inputs.

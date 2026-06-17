# token_bucket — pseudocode plan

Verdict: stateful numerical algorithm — bucket level is a mutated invariant, refill
depends on elapsed time between events, clamping at both bounds. Planning first.

## Data & invariants
- `tokens`: real number, the current bucket level. INVARIANT: always in [0, capacity].
- `last_t`: timestamp of the previous event (for elapsed-time refill).
- Events: list of (timestamp, cost), timestamps non-decreasing.
- Output: list of booleans, one per event, same order.

## Control flow
```
tokens   ← capacity            # bucket starts full
last_t   ← timestamp of first event (so first event sees 0 elapsed)
results  ← empty

for each (t, cost) in events:
    elapsed ← t - last_t       # ≥ 0 because timestamps non-decreasing
    tokens  ← min(capacity, tokens + refill_per_sec * elapsed)   # refill, clamp top
    last_t  ← t

    if tokens >= cost:
        tokens ← tokens - cost   # spend (stays ≥ 0 since tokens ≥ cost)
        append True
    else:
        append False             # deny, bucket unchanged

return results
```

Note: clamp at top happens during refill. Bottom is guarded by the `tokens >= cost`
check before subtracting, so tokens never goes negative. No explicit lower clamp needed.

## Edge cases & failure modes
- Empty events           → return empty list (loop body never runs; init of last_t must
                           not crash → guard: if no events, return []).
- First event            → elapsed = 0 (last_t = first ts), no refill, sees full bucket.
- Multiple events same t  → elapsed = 0, no refill between them (matches example t=0,t=0).
- cost == 0              → tokens >= 0 always true → always allowed, no change.
- cost > capacity        → can never be satisfied even when full → always deny.
- Refill overshoots cap   → min() clamps to capacity (example: refill 2 over long gap).
- Real-number arithmetic  → no rounding; use float comparison directly (`>=`).

## Interface contract
- Pure w.r.t. inputs (events list not mutated).
- Returns list[bool] of length len(events).
- No exceptions for valid input; empty input → [].

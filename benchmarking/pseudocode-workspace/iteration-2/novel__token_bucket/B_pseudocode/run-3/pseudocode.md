# token_bucket — pseudocode plan

Verdict: numerical state with an invariant (level ∈ [0, capacity]) plus
order-dependent refill timing. Subtle-bug-prone, so plan first.

## Data & invariants
- `level`: real number, current tokens. INVARIANT: 0 ≤ level ≤ capacity at all times.
- `last_t`: timestamp of the previous event (for elapsed computation).
- events given in non-decreasing timestamp order (elapsed ≥ 0 always).
- Output: list[bool], one entry per event, same order.

## Control flow
```
level   ← capacity            # starts full
last_t  ← (timestamp of first event, or 0 — see below)
result  ← []

for each (t, cost) in events:
    elapsed ← t - last_t            # ≥ 0 by ordering assumption
    level   ← min(capacity, level + refill_per_sec * elapsed)   # clamp top
    last_t  ← t
    if level >= cost:
        level ← level - cost        # allow; level stays ≥ 0 since level ≥ cost
        result.append(True)
    else:
        result.append(False)        # deny; level unchanged
return result
```

Init of last_t: set to first event's timestamp so the first refill is 0
(bucket already full, nothing to add). Equivalently initialize before loop
from events[0][0]. For the empty list, return [] immediately.

## Edge cases & failure modes
- empty events            → return []
- first event             → elapsed 0, level stays at capacity (full start)
- two events same timestamp→ elapsed 0, no refill between them (matches example: 0,5 then 0,5)
- cost == level exactly   → `>=` allows it, level → 0 (boundary uses ≥, not >)
- cost > capacity         → can never be allowed; refill clamps at capacity < cost → deny
- cost == 0               → always allowed (level ≥ 0 ≥ 0), subtract 0
- large elapsed           → min() clamps so level never exceeds capacity
- denied event            → level untouched, last_t still advances to t (refill already applied)

## Interface contract
- pure; does not mutate `events`.
- returns new list of bool, length == len(events).
- no rounding; floats used directly.

## Example check
capacity=10, refill=1, events=[(0,5),(0,5),(0,1),(2,2)]
- (0,5): elapsed0, level10→ allow, level5 → True
- (0,5): elapsed0, level5 → allow, level0 → True
- (0,1): elapsed0, level0 < 1 → deny → False
- (2,2): elapsed2, level0+2=2 ≤10 → 2≥2 allow, level0 → True
=> [True, True, False, True] ✓

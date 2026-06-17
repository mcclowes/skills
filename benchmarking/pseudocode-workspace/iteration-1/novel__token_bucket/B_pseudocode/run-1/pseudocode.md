# token_bucket — pseudocode plan

Verdict: numerical invariant + state-carrying loop (bucket level clamped to [0, capacity], refill over elapsed time). Logic-heavy, plan first.

## Data & invariants
- `level`: real number, current tokens. INVARIANT: `0 <= level <= capacity` at all times.
- `last_t`: timestamp of previous event (for elapsed calc). Starts at first event's timestamp (no refill before first event).
- `capacity`, `refill_per_sec`: constants.
- events: list of (timestamp, cost), timestamps non-decreasing.
- Output: list[bool], one per event, same order.

## Control flow
```
level ← capacity                 # bucket starts full
last_t ← (timestamp of first event, if any)   # so first refill = 0
result ← empty list

for each (t, cost) in events:
    elapsed ← t - last_t          # >= 0 by non-decreasing assumption
    level ← min(capacity, level + refill_per_sec * elapsed)   # refill, clamp high
    last_t ← t                    # advance clock regardless of allow/deny
    if level >= cost:
        level ← level - cost      # allow, spend
        append True
    else:
        append False              # deny, leave level unchanged
result
```

## Edge cases & failure modes
- empty events            → return empty list (loop body never runs).
- first event             → elapsed = t - last_t = 0, so no spurious refill before first event.
- multiple events same t  → elapsed = 0, no refill between them (matches example: two cost-5 at t=0 drain bucket).
- cost == level exactly   → `level >= cost` true → ALLOW (boundary uses >=, e.g. third example cost matches).
- cost == 0               → always allowed, level unchanged effectively (level - 0).
- refill overshoot        → min(capacity, ...) clamps so level never exceeds capacity.
- deny does NOT consume   → level untouched on deny; later events can still be served.
- floating point          → keep as real numbers, no rounding; use >= comparison directly.
- last_t must advance even on deny, so subsequent elapsed is measured from current event.

## Interface contract
- Pure function; does not mutate `events`.
- Returns new list[bool] of length == len(events).
- No exceptions for normal inputs. Assumes timestamps non-decreasing (per spec).

## Check against example
capacity=10, refill=1, events=[(0,5),(0,5),(0,1),(2,2)], start level=10, last_t=0
- (0,5): elapsed 0, level 10, 10>=5 → allow, level 5. [True]
- (0,5): elapsed 0, level 5, 5>=5 → allow, level 0. [True]
- (0,1): elapsed 0, level 0, 0>=1 false → deny, level 0. [False]
- (2,2): elapsed 2, level min(10, 0+2)=2, 2>=2 → allow, level 0. [True]
→ [True, True, False, True] ✓

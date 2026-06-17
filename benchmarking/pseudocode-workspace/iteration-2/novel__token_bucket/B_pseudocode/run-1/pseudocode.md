# token_bucket plan

Verdict: numerical state machine with an invariant (level in [0, capacity]) and
time-elapsed refill — subtle enough to plan first.

## Data & invariants
- level: real, current tokens. Invariant: 0 ≤ level ≤ capacity at all times.
- last_ts: timestamp of the previous event (start = first event's time, but
  more robustly: track and refill by delta; first event has delta 0).
- events: list of (timestamp, cost), timestamps non-decreasing.
- Output: list of bool, one per event.

## Control flow
level ← capacity
last_ts ← None
results ← []
for (ts, cost) in events:
    if last_ts is not None:
        elapsed ← ts - last_ts          # ≥ 0 by precondition
        level ← min(capacity, level + refill_per_sec * elapsed)
    last_ts ← ts
    if level >= cost:
        level ← level - cost            # allow
        append True
    else:
        append False                    # deny, level unchanged
return results

## Edge cases & failure modes
- empty events            → return []
- first event: no prior, delta 0, no refill; bucket starts full.
- same-timestamp events   → elapsed 0, no refill (matches example: two cost-5 at t=0).
- cost == level exactly   → allow (use >=).
- cost == 0               → always allowed, level unchanged (>= holds).
- refill clamps at capacity via min, so level never exceeds capacity.
- denied event leaves level untouched, so a later cheaper event can pass.
- float: no rounding; direct arithmetic keeps level real.

## Interface contract
- Pure; does not mutate input. Returns new list of bool.
- Assumes timestamps non-decreasing (per spec); no validation.

# token_bucket — plan

Verdict: numerical state with an invariant (level stays in [0, capacity]) and
time-elapsed refill ordering. Planning first.

## Data & invariants
- `level`: real number, current tokens. Invariant: 0 ≤ level ≤ capacity at all times.
- `last_ts`: timestamp of the previous processed event (for elapsed calc).
- events given in non-decreasing timestamp order, so elapsed ≥ 0 always.
- Output: list[bool], one per event, same order.

## Control flow
```
level ← capacity            # starts full
last_ts ← timestamp of first event (or unused until first event)
result ← []
for each (ts, cost) in events:
    elapsed ← ts - last_ts          # ≥ 0 by ordering; for first event elapsed=0
    level ← min(capacity, level + refill_per_sec * elapsed)   # refill, cap
    if level >= cost:
        level ← level - cost        # ALLOW, spend
        result.append(True)
    else:
        result.append(False)        # DENY, leave unchanged
    last_ts ← ts
return result
```
Initialise last_ts to first event's ts so the first elapsed is 0 (no refill,
bucket already full). Handle by setting last_ts before loop, or special-case
first iteration.

## Edge cases & failure modes
- empty events → return [] (loop body never runs).
- first event: elapsed must be 0 → set last_ts = events[0][0] before loop.
- multiple events same timestamp → elapsed 0, no refill between them (matches example: two cost-5 at t=0 drain then third denied).
- cost == level exactly → allow (use >=, not >).
- cost 0 → always allowed, no change.
- refill never pushes above capacity → min() clamp keeps invariant.
- denied event leaves level unchanged (don't subtract).

## Interface contract
Pure-ish: returns new list, does not mutate inputs. No error handling specified;
assumes well-formed numeric inputs and ordered timestamps.

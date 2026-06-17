def token_bucket(capacity, refill_per_sec, events):
    """A token-bucket rate limiter."""
    result = []
    level = capacity
    last_ts = events[0][0] if events else 0
    for ts, cost in events:
        elapsed = ts - last_ts
        level = min(capacity, level + refill_per_sec * elapsed)
        if level >= cost:
            level -= cost
            result.append(True)
        else:
            result.append(False)
        last_ts = ts
    return result

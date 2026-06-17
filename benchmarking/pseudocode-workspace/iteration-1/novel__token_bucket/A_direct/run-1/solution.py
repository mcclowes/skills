def token_bucket(capacity, refill_per_sec, events):
    tokens = float(capacity)
    last_ts = None
    results = []
    for ts, cost in events:
        if last_ts is not None:
            elapsed = ts - last_ts
            tokens = min(capacity, tokens + refill_per_sec * elapsed)
        last_ts = ts
        if tokens >= cost:
            tokens -= cost
            results.append(True)
        else:
            results.append(False)
    return results

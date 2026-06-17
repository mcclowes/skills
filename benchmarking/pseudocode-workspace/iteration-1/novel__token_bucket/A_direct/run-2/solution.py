def token_bucket(capacity, refill_per_sec, events):
    tokens = capacity
    last_time = None
    results = []
    for timestamp, cost in events:
        if last_time is not None:
            elapsed = timestamp - last_time
            tokens = min(capacity, tokens + refill_per_sec * elapsed)
        last_time = timestamp
        if tokens >= cost:
            tokens -= cost
            results.append(True)
        else:
            results.append(False)
    return results

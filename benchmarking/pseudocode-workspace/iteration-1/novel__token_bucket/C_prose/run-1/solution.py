def token_bucket(capacity, refill_per_sec, events):
    """A token-bucket rate limiter.

    The bucket starts full (capacity tokens). `events` is a list of
    (timestamp_seconds, cost) tuples, given in non-decreasing timestamp order.
    Before each event, refill the bucket based on elapsed time since the last
    event: add refill_per_sec * elapsed tokens, but never exceed `capacity`.
    Then, if the bucket has at least `cost` tokens, ALLOW the event and subtract
    cost; otherwise DENY it and leave the bucket unchanged.

    Returns a list of booleans, one per event.
    """
    results = []
    level = capacity
    last_ts = None

    for ts, cost in events:
        if last_ts is None:
            last_ts = ts
        elapsed = ts - last_ts
        level = min(capacity, level + refill_per_sec * elapsed)
        last_ts = ts

        if level >= cost:
            level -= cost
            results.append(True)
        else:
            results.append(False)

    return results

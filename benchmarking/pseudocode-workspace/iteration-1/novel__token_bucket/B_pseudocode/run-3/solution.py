def token_bucket(capacity, refill_per_sec, events):
    """A token-bucket rate limiter.

    The bucket starts full (capacity tokens). `events` is a list of
    (timestamp_seconds, cost) tuples, given in non-decreasing timestamp order.
    Before each event, refill the bucket based on elapsed time since the last
    event: add refill_per_sec * elapsed tokens, but never exceed `capacity`.
    Then, if the bucket has at least `cost` tokens, ALLOW the event and subtract
    cost; otherwise DENY it and leave the bucket unchanged.

    Tokens are real numbers (no rounding). The bucket level must always stay in
    the range [0, capacity].

    Return a list of booleans, one per event: True if allowed, False if denied.
    """
    if not events:
        return []

    tokens = capacity
    last_t = events[0][0]
    results = []

    for t, cost in events:
        elapsed = t - last_t
        tokens = min(capacity, tokens + refill_per_sec * elapsed)
        last_t = t

        if tokens >= cost:
            tokens -= cost
            results.append(True)
        else:
            results.append(False)

    return results

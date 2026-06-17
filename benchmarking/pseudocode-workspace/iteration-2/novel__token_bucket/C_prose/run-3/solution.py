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
    level = capacity
    last_timestamp = None
    results = []

    for timestamp, cost in events:
        if last_timestamp is not None:
            elapsed = timestamp - last_timestamp
            level = min(capacity, level + refill_per_sec * elapsed)
        last_timestamp = timestamp

        if level >= cost:
            level -= cost
            results.append(True)
        else:
            results.append(False)

    return results

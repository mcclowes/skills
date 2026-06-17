#!/usr/bin/env python3
"""Novel, contamination-free Tier-H tasks authored for the pseudocode benchmark.

These are not in any public dataset. Each is logic-heavy in the way the thesis
targets: a subtle invariant, a boundary, an ordering, or a parse where
correct-looking code is routinely subtly wrong. Each ships a base suite (happy
path) and a plus suite (adversarial edges) so we can report the edge-case gap
separately — that gap is where the thesis predicts the pseudocode arm wins.
"""
import json

TASKS = []


def add(task_id, entry_point, prompt, base_test, plus_test):
    TASKS.append({
        "task_id": task_id, "tier": "H", "entry_point": entry_point,
        "prompt": prompt, "base_test": base_test, "plus_test": plus_test,
    })


# ── Task 1: token bucket rate limiter (state machine + invariant) ─────────────
add(
    "novel/token_bucket",
    "token_bucket",
    '''def token_bucket(capacity, refill_per_sec, events):
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

    Example:
        capacity=10, refill_per_sec=1
        events=[(0,5),(0,5),(0,1),(2,2)]
        -> [True, True, False, True]
        (at t=0 spend 5 then 5 -> empty; third needs 1 -> deny;
         by t=2 refilled 2 tokens -> allow cost 2)
    """
''',
    # base: the docstring example + a couple of straightforward cases
    '''
def check(candidate):
    assert candidate(10, 1, [(0,5),(0,5),(0,1),(2,2)]) == [True, True, False, True]
    assert candidate(5, 2, [(0,5)]) == [True]
    assert candidate(5, 2, [(0,5),(0,1)]) == [True, False]
    assert candidate(10, 1, []) == []
''',
    # plus: refill cap (no overflow), exact-boundary spend, zero cost, large gap,
    # repeated same-timestamp events, cost exactly equal to level.
    '''
def check(candidate):
    # starts full; a long initial gap must NOT overflow above capacity
    assert candidate(10, 1, [(100, 10)]) == [True]
    assert candidate(10, 1, [(100, 11)]) == [False]
    # exact-boundary: spend down to exactly 0, then need same amount after refill
    assert candidate(4, 1, [(0,4),(4,4)]) == [True, True]
    assert candidate(4, 1, [(0,4),(3,4)]) == [True, False]
    # zero-cost events are always allowed and change nothing
    assert candidate(3, 1, [(0,3),(0,0),(0,1)]) == [True, True, False]
    # multiple events at the same timestamp: no phantom refill between them
    assert candidate(2, 5, [(0,1),(0,1),(0,1)]) == [True, True, False]
    # cost exactly equal to current level is allowed (>=, not >)
    assert candidate(7, 0, [(0,7)]) == [True]
    assert candidate(7, 0, [(0,7),(9,1)]) == [True, False]  # no refill, stays empty
    # fractional refill accumulates correctly
    assert candidate(10, 0.5, [(0,10),(1,1)]) == [True, False]
    assert candidate(10, 0.5, [(0,10),(2,1)]) == [True, True]
''',
)


# ── Task 2: Elo update with margin-of-victory swing (numerical) ───────────────
add(
    "novel/elo_swing",
    "elo_swing",
    '''def elo_swing(rating_a, rating_b, score_a, score_b, k=32):
    """Compute player A's new Elo rating after a match, with a
    margin-of-victory multiplier.

    Standard expected score for A:
        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    Actual result for A:
        win  -> 1.0   (score_a > score_b)
        draw -> 0.5   (score_a == score_b)
        loss -> 0.0   (score_a < score_b)

    Margin multiplier (amplifies decisive results, never below 1):
        margin = abs(score_a - score_b)
        mult   = log(margin + 1) base e, but at least 1.0  ->  max(1.0, ln(margin+1))

    New rating for A:
        rating_a + k * mult * (actual_a - expected_a)

    Return the new rating as a float (do not round). A draw must leave the
    multiplier irrelevant only insofar as the formula dictates — apply it as
    written.
    """
''',
    '''
import math
def check(candidate):
    # even ratings, A wins by 1: expected 0.5, mult = max(1, ln2)=1.0
    got = candidate(1500, 1500, 2, 1, k=32)
    assert abs(got - (1500 + 32*1.0*(1.0-0.5))) < 1e-9, got
    # even ratings, draw: actual 0.5 == expected 0.5 -> no change
    assert abs(candidate(1500,1500,1,1,k=32) - 1500) < 1e-9
''',
    '''
import math
def check(candidate):
    # big margin amplifies: margin 9 -> mult ln(10)
    exp = 1/(1+10**((1500-1500)/400))
    mult = max(1.0, math.log(10))
    assert abs(candidate(1500,1500,10,1,k=32) - (1500+32*mult*(1.0-exp))) < 1e-6
    # margin 0 (draw) -> mult max(1, ln1=0) = 1.0, but actual-expected may be nonzero
    a,b = 1400,1600
    exp = 1/(1+10**((b-a)/400))
    assert abs(candidate(a,b,3,3,k=32) - (a+32*1.0*(0.5-exp))) < 1e-6
    # loss by big margin for the lower-rated: should drop, mult applies
    a,b=1600,1400
    exp=1/(1+10**((b-a)/400))
    mult=max(1.0, math.log(8))
    assert abs(candidate(a,b,0,7,k=32) - (a+32*mult*(0.0-exp))) < 1e-6
    # k=0 -> rating never changes regardless of result
    assert abs(candidate(1200,1800,9,0,k=0) - 1200) < 1e-9
    # margin 1 win: ln2 < 1 so mult clamps to 1.0 (not ln2)
    a,b=1500,1500
    exp=0.5
    assert abs(candidate(a,b,5,4,k=32) - (a+32*1.0*(1.0-exp))) < 1e-9
''',
)


# ── Task 3: tiny arithmetic expression evaluator (parser + precedence) ────────
add(
    "novel/eval_expr",
    "eval_expr",
    '''def eval_expr(expr):
    """Evaluate a simple arithmetic expression and return an integer or float.

    Supported: non-negative integers, binary + - * /, parentheses, and spaces.
    Standard precedence: * and / bind tighter than + and -; left-associative;
    parentheses override. Division is true division (/ yields a float).

    No unary minus, no exponent. The input is always well-formed.

    Examples:
        eval_expr("2 + 3 * 4")      -> 14
        eval_expr("(2 + 3) * 4")    -> 20
        eval_expr("10 - 2 - 3")     -> 5      (left-assoc, not 11)
        eval_expr("8 / 4 / 2")      -> 1.0
    """
''',
    '''
def check(candidate):
    assert candidate("2 + 3 * 4") == 14
    assert candidate("(2 + 3) * 4") == 20
    assert candidate("10 - 2 - 3") == 5
    assert candidate("8 / 4 / 2") == 1.0
    assert candidate("7") == 7
''',
    '''
def check(candidate):
    # left-associativity of subtraction and division (the classic bug)
    assert candidate("100 - 10 - 5 - 1") == 84
    assert candidate("64 / 4 / 2 / 2") == 4.0
    # nested parens and precedence interplay
    assert candidate("2 * (3 + 4 * (1 + 1))") == 22
    assert candidate("((1 + 2) * (3 + 4))") == 21
    # multi-digit numbers, no spaces
    assert candidate("12*12+1") == 145
    # precedence: * before +, both directions
    assert candidate("1 + 2 * 3 + 4") == 11
    assert candidate("2 * 3 + 4 * 5") == 26
    # parens forcing low-precedence first
    assert candidate("(10 - 2) * (10 - 8)") == 16
    # division producing float propagates through addition
    assert candidate("1 + 9 / 2") == 5.5
    # deeply left-nested
    assert candidate("1 - 1 - 1 - 1 - 1") == -3
''',
)


# ── Task 4: merge weighted intervals, summing weights on overlap (invariant) ──
add(
    "novel/merge_weighted_intervals",
    "merge_weighted_intervals",
    '''def merge_weighted_intervals(intervals):
    """Merge overlapping half-open intervals, summing their weights.

    Each input is a tuple (start, end, weight) with start < end and weight a
    number. Intervals are half-open [start, end): two intervals that merely
    touch (one ends exactly where the next begins) do NOT overlap.

    Merge any intervals that overlap (share more than a single point) into one
    interval spanning [min start, max end), whose weight is the SUM of the
    weights of all intervals merged into it. Overlap is transitive: if A overlaps
    B and B overlaps C, all three merge even if A and C are disjoint.

    Return the merged intervals as a list of (start, end, weight) tuples sorted
    by start ascending. Input is not necessarily sorted.

    Example:
        [(1,3,5),(2,4,1),(6,8,2)] -> [(1,4,6),(6,8,2)]
        [(1,2,1),(2,3,1)]         -> [(1,2,1),(2,3,1)]   (touching, not merged)
    """
''',
    '''
def check(candidate):
    assert candidate([(1,3,5),(2,4,1),(6,8,2)]) == [(1,4,6),(6,8,2)]
    assert candidate([(1,2,1),(2,3,1)]) == [(1,2,1),(2,3,1)]
    assert candidate([]) == []
    assert candidate([(5,10,3)]) == [(5,10,3)]
''',
    '''
def check(candidate):
    # touching boundary must NOT merge (half-open: > not >=)
    assert candidate([(0,1,1),(1,2,1),(2,3,1)]) == [(0,1,1),(1,2,1),(2,3,1)]
    # transitive merge via a connecting middle interval
    assert candidate([(1,5,1),(10,15,1),(4,11,10)]) == [(1,15,12)]
    # fully nested interval contributes weight, span unchanged
    assert candidate([(1,10,2),(3,4,5)]) == [(1,10,7)]
    # unsorted input
    assert candidate([(6,8,2),(2,4,1),(1,3,5)]) == [(1,4,6),(6,8,2)]
    # negative weights sum correctly
    assert candidate([(1,4,5),(2,3,-2)]) == [(1,4,3)]
    # overlap of exactly more-than-a-point merges; 1-point would not
    assert candidate([(1,3,1),(2,5,1)]) == [(1,5,2)]
    # duplicate identical intervals merge and sum
    assert candidate([(1,2,1),(1,2,1)]) == [(1,2,2)]
    # chain where each only overlaps its neighbour
    assert candidate([(1,3,1),(2,4,1),(3,5,1)]) == [(1,5,3)]
''',
)


def main():
    with open("/tmp/corpus_novel.json", "w") as f:
        json.dump(TASKS, f, indent=2)
    print(f"wrote {len(TASKS)} novel tasks")
    # self-check: solutions must pass their own suites (sanity of the tests)


if __name__ == "__main__":
    main()

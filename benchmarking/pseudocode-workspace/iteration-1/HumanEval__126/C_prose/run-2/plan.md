# Plan for is_sorted

## Input/output contract

`is_sorted(lst)` takes a list of non-negative integers and returns a boolean.
It returns `True` when the list is sorted in ascending (non-decreasing) order
*and* no value appears more than twice; otherwise it returns `False`.

## Data involved

A single Python list of integers. We never mutate it. We need two independent
checks: monotonicity of the ordering, and a cap on how many times any single
value may repeat. The problem statement says "more than 1 duplicate of the same
number" should fail — interpreting the provided examples, a value may appear at
most twice. `[1, 2, 2, 3, 3, 4]` is valid (each repeated value appears twice),
while `[1, 2, 2, 2, 3, 4]` is invalid (a value appears three times, i.e. has
more than one duplicate).

## Algorithm steps

1. Check ordering: iterate over adjacent pairs `(lst[i], lst[i+1])`. If any
   `lst[i] > lst[i+1]`, the list is not ascending, so return `False`.
2. Check duplicate frequency: count occurrences of each value using a
   `Counter`. If any value's count exceeds 2, return `False`.
3. If both checks pass, return `True`.

## Edge cases

- Empty list: no adjacent pairs and no counts exceed 2, so returns `True`
  vacuously.
- Single element `[5]`: trivially sorted, returns `True`.
- Equal adjacent values like `[1, 2, 2, 3]`: allowed by `<=`, and the count cap
  of 2 permits a single duplicate.
- Three or more of the same value: rejected by the count check even if the list
  is otherwise sorted.

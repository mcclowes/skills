# Plan for `is_sorted`

## Input/output contract
- Input: `lst`, a list of non-negative integers (the problem guarantees no negative numbers and only integers).
- Output: a boolean. `True` if the list is sorted in non-decreasing (ascending) order AND no value appears more than twice; otherwise `False`.

## Understanding the requirements
There are two independent conditions, both of which must hold for `True`:
1. **Ascending order**: every element must be less than or equal to the next element. Equal adjacent values are allowed for ordering purposes (the example `[1, 2, 2, 3, 3, 4]` returns `True`), so the comparison is `<=`, not strict `<`.
2. **Duplicate limit**: "more than 1 duplicate of the same number" means a number appearing three or more times. Two copies of a number are fine (`[1, 2, 2, 3, 3, 4]` is `True`), but three or more copies make it `False` (`[1, 2, 2, 2, 3, 4]` is `False`). So any count `> 2` for any value fails.

## Algorithm steps
1. Count the occurrences of each value using `collections.Counter`. If any value has a count greater than 2, return `False`.
2. Check ordering: iterate over adjacent pairs and confirm each element is `<= ` the following element. If any pair violates this, return `False`.
3. If both checks pass, return `True`.

## Edge cases
- Single-element list (`[5]`): no adjacent pairs, no duplicates, returns `True`.
- Empty list: trivially sorted with no duplicates, returns `True`.
- Exactly two equal values: allowed, count is 2 which is not `> 2`.
- Three or more equal values: fails the duplicate check even if technically "in order".

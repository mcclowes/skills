# Plan for is_sorted

## Input/output contract
The function `is_sorted(lst)` takes a list of non-negative integers and returns a
boolean. It returns `True` when the list is sorted in non-decreasing (ascending)
order AND no value appears three or more times. Otherwise it returns `False`.

## Data involved
A single list of integers, possibly empty, possibly with duplicates. Per the
problem statement we may assume there are no negative numbers and every element is
an integer, so no type validation is required.

## Algorithm steps
1. Check ascending order. Iterate over adjacent pairs and confirm that each element
   is less than or equal to the next (`lst[i] <= lst[i+1]`). Using `<=` rather than
   `<` correctly permits duplicates, which the examples show are allowed when not
   excessive. If any pair violates this, the list is not sorted, so return `False`.
2. Check duplicate frequency. Count how many times each value occurs. If any value
   occurs more than twice (a strict "more than 1 duplicate", meaning three or more
   total copies of the same number), return `False`.
3. If both checks pass, return `True`.

## Interpreting "more than 1 duplicate"
The example `[1, 2, 2, 3, 3, 4]` is `True` (two copies each are fine), while
`[1, 2, 2, 2, 3, 4]` is `False` (three copies of 2). So the rule is: a count
strictly greater than 2 for any value makes the result `False`.

## Edge cases
- Empty list: vacuously sorted with no duplicates, return `True`.
- Single element `[5]`: sorted, no duplicates, return `True`.
- Two equal elements `[2, 2]`: sorted and only two copies, return `True`.
- Sorting and the duplicate rule are independent: an unsorted list fails even if no
  value repeats three times.

## Implementation approach
Use `collections.Counter` to tally occurrences and a simple pairwise comparison to
verify order. Both are O(n).

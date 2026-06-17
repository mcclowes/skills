# Plan: move_one_ball

## Input/output contract
- Input: `arr`, a list of N integers with unique elements, randomly ordered.
- Output: a boolean. Return `True` if the array can be sorted into
  non-decreasing order using any number of right-shift (rotate-right)
  operations; otherwise `False`. An empty array returns `True`.

## Key insight
A right shift is a cyclic rotation. Performing it any number of times produces
every cyclic rotation of the array. The question is therefore: is the sorted
version of `arr` one of the cyclic rotations of `arr`?

For a sequence to be a rotation of its own sorted order, it must be "sorted
with at most one wrap-around break." That is, when you scan the array
circularly, the number of positions where an element is greater than its
successor (with the last element compared to the first) must be at most one.

- If there are zero such break points, the array is already sorted.
- If there is exactly one break point, rotating so the array starts right after
  that break yields the sorted array.
- If there are two or more break points, no rotation can sort it.

## Algorithm steps
1. If `arr` is empty, return `True`.
2. Count `breaks`: iterate over all N indices, comparing `arr[i]` to
   `arr[(i + 1) % N]`. Increment `breaks` each time `arr[i] > arr[next]`.
3. Return `breaks <= 1`.

## Edge cases
- Empty array: handled explicitly, returns `True`.
- Single element: zero breaks, returns `True`.
- Already sorted: zero breaks, returns `True`.
- Sorted-rotated (e.g. `[3,4,5,1,2]`): exactly one break, returns `True`.
- Genuinely unsortable (e.g. `[3,5,4,1,2]`): two breaks, returns `False`.
- Uniqueness is guaranteed, so no need to handle equal adjacent values.

This runs in O(N) time and O(1) extra space.

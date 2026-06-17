# Plan: move_one_ball

## Contract
- Input: `arr`, a list of N integers with unique elements, randomly ordered.
- Output: a boolean. `True` if the array can be sorted into non-decreasing order using only right-shift (rotation) operations; otherwise `False`.

## Key insight
A right shift is a cyclic rotation. Performing any number of right shifts produces some rotation of the original array. The question therefore reduces to: is any rotation of `arr` equal to the fully sorted version of `arr`?

A unique-element array is some rotation of its sorted form if and only if it has at most one "descent" — a position `i` where `arr[i] > arr[i+1]` — when we also consider the wrap-around edge (last element vs first element). A sorted array has zero internal descents; a rotated sorted array has exactly one internal descent (at the rotation seam). If there are two or more internal descents, no rotation can sort it.

## Algorithm steps
1. If `arr` is empty, return `True`.
2. Count the number of indices `i` in `0..N-2` where `arr[i] > arr[i+1]` (internal descents).
3. Additionally account for the wrap-around: a valid rotation requires that the array wraps cleanly, i.e. the last element is not greater than the first (when there is exactly one seam). The clean check: count internal descents; if 0, it's already sorted → True. If exactly 1, the array is sortable only if `arr[-1] <= arr[0]` (the seam wraps correctly). If more than 1, → False.

## Edge cases
- Empty array → `True`.
- Single element → 0 descents → `True`.
- Already sorted → `True`.
- Strictly decreasing of length > 2 → multiple descents → `False`.

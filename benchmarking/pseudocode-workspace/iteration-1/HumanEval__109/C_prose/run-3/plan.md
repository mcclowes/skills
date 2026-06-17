# Plan: move_one_ball

## Input/output contract
- Input: `arr`, a list of N integers with unique elements, randomly ordered.
- Output: a boolean. Return `True` if the array can be sorted into non-decreasing
  order using only right-shift (cyclic rotation) operations applied any number of
  times; otherwise return `False`. An empty array returns `True`.

## Key insight
A right-shift operation is a cyclic rotation: the last element moves to index 0 and
everything else slides right by one. Applying right shifts any number of times
produces every cyclic rotation of the array. So the question reduces to: is some
cyclic rotation of `arr` equal to the fully sorted version of `arr`?

A sorted array is a rotation of `arr` if and only if the array is already
"rotated-sorted" — meaning it has at most one position where an element is greater
than the element that follows it (treating the array as circular, i.e. comparing the
last element with the first). If there are zero such "descents," the array is already
sorted. If there is exactly one descent, rotating to break at that point yields the
sorted order. If there are two or more descents, no rotation can produce a fully
sorted array, so return `False`.

## Algorithm steps
1. If `arr` is empty, return `True`.
2. Count the number of indices `i` (0-based, comparing `arr[i]` with `arr[i+1]`)
   where `arr[i] > arr[i+1]`.
3. Also compare the wrap-around pair: last element vs first element.
4. If the total count of such descents is at most 1, return `True`; else `False`.

## Edge cases
- Empty array: return `True` (handled first).
- Single element: zero descents, return `True`.
- Already sorted array: zero internal descents, wrap-around may or may not count but
  total stays at most 1, returns `True`.
- Two or more break points: returns `False`.

This is O(N) time and O(1) extra space.

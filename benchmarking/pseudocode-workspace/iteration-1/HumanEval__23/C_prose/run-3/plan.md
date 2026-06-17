# Plan: strlen

## Contract
- Input: a single parameter `string` of type `str`. It may be empty, contain
  any Unicode characters, whitespace, punctuation, or multi-byte characters.
- Output: an `int` giving the number of characters in the string.
- The function is pure: no side effects, no mutation, no I/O.

## Data involved
The only data is the input string itself. Conceptually a string is an ordered
sequence of characters, and the task is to report how many elements that
sequence contains. In Python, "character count" means the number of code points
in the `str`, which is exactly what the built-in `len` reports.

## Algorithm
This is a direct length query. The simplest, most reliable approach is to
return `len(string)`, which runs in O(1) time because CPython stores the
length alongside the string object. There is no need to iterate manually or
maintain a running counter; doing so would only introduce risk and slower
behavior with no benefit.

## Edge cases
- Empty string `''` -> must return `0`. `len('')` returns `0`, satisfying the
  first docstring example.
- Normal strings like `'abc'` -> returns `3`, matching the second example.
- Strings with spaces, tabs, or punctuation: each such character is counted,
  consistent with `len`'s definition.
- Unicode characters: counted as individual code points, which is the standard
  expectation for `len` on a `str`.

## Verification
The two documented examples (`''` -> 0, `'abc'` -> 3) are both satisfied by
returning `len(string)`, so the implementation matches the specified contract.

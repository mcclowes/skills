# Plan: strlen

## Input/output contract
The function `strlen` takes a single argument `string` of type `str` and returns
an `int`: the number of characters in that string. For the empty string it must
return `0`; for `'abc'` it returns `3`.

## Data involved
The only data is the input string. In Python, a `str` is a sequence of Unicode
code points, and its length is the count of those code points. No external data,
state, or side effects are involved.

## Algorithm steps
This is a direct length query. Python's built-in `len()` returns the number of
items in a sequence, which for a string is exactly its character count in O(1)
time, since CPython stores the length alongside the object rather than scanning.
The implementation simply returns `len(string)`.

## Edge cases
- Empty string `''` -> `len` returns `0`, matching the first docstring example.
- Single-character strings -> returns `1`.
- Strings containing whitespace, punctuation, or non-ASCII/Unicode characters ->
  `len` counts each code point, which is the expected behaviour here.
- Multi-byte emoji composed of multiple code points would count each code point
  separately, but that matches Python's standard string-length semantics and the
  spec's intent.

Per the contract the argument is always a `str`, so no type coercion or `None`
handling is required. The solution is a single clear expression with no branching,
which keeps it correct and trivially readable.

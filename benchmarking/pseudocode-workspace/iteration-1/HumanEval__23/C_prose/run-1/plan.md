# Plan for strlen

## Input/output contract
The function `strlen` takes a single parameter `string` of type `str` and
returns an `int`. The return value is the number of characters contained in
the input string. For an empty string the result is `0`; for `'abc'` the
result is `3`.

## Data involved
The only data is the input string itself. Python strings are sequences of
Unicode code points, and the goal is to count how many such code points the
string contains. No external state, files, or auxiliary data structures are
needed.

## Algorithm steps
Python provides the built-in `len()` function, which returns the number of
items in a container — for a string that is exactly the number of characters
(code points). The implementation therefore reduces to a single step: return
`len(string)`. This is O(1) because CPython stores the length of a string
alongside the object rather than recomputing it by scanning.

## Edge cases
- Empty string `''`: `len('')` correctly returns `0`, matching the docstring.
- Strings with spaces or punctuation: every character, including whitespace,
  is counted.
- Multi-byte / Unicode characters: `len` counts code points, which is the
  expected character count for typical inputs.

Because the signature annotates `string` as `str`, no defensive type checking
is required; we rely on the documented contract that a string is passed.

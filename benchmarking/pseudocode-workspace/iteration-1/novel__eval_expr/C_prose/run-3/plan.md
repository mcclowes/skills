# Plan: eval_expr

## Contract
- Input: `expr`, a string containing a well-formed arithmetic expression made of non-negative integers, the binary operators `+ - * /`, parentheses, and spaces.
- Output: a number — an `int` or `float`. Division always uses true division, so any `/` produces a float; pure integer addition/subtraction/multiplication stays `int`.
- Guarantees: input is always well-formed, so no error handling for malformed input is required. There is no unary minus and no exponent.

## Algorithm
I'll use a classic two-phase approach: tokenize, then parse with a recursive-descent grammar that encodes precedence and left-associativity.

1. **Tokenize.** Walk the string character by character. Skip spaces. Group consecutive digits into a single integer token. Emit each operator and parenthesis as its own token. Numbers become Python `int`s.

2. **Parse / evaluate** with three grammar levels, evaluating as we go:
   - `expression := term (("+" | "-") term)*`
   - `term := factor (("*" | "/") factor)*`
   - `factor := NUMBER | "(" expression ")"`

   A shared position index tracks the current token. Each `*` loop consumes operators left to right, applying them immediately, which yields correct left-associativity (`10 - 2 - 3 == 5`, `8 / 4 / 2 == 1.0`). Putting `*`/`/` one level below `+`/`-` gives standard precedence; parentheses recurse back to `expression`, overriding it.

## Edge cases
- Multi-digit numbers (digit grouping).
- Arbitrary nested parentheses (recursion handles depth).
- Mixed spacing, including none.
- Single number with no operator.
- `/` producing float vs. int-only arithmetic staying int — natural from Python's `+ - *` on ints and `/` always returning float.

# Plan: eval_expr

## Input/output contract
`eval_expr(expr: str)` takes a well-formed arithmetic expression string and returns an
`int` or `float`. The grammar supports non-negative integer literals, the binary operators
`+ - * /`, parentheses, and arbitrary spaces. There is no unary minus and no exponent, and
the input is guaranteed well-formed, so I do not need to surface syntax errors. Division is
true division and therefore always yields a `float` (matching Python's `/`); the other
operators preserve `int` results where Python naturally does.

## Algorithm
I'll use a classic two-phase approach: tokenize, then parse with a recursive-descent parser
that encodes precedence and left-associativity directly in its structure.

1. **Tokenize**: walk the string character by character. Skip spaces. Accumulate consecutive
   digits into a single integer token. Emit `+ - * / ( )` as individual operator/paren tokens.
2. **Parse** with three mutually recursive levels reflecting precedence, using a shared
   position index:
   - `parse_expr`: parses a `term`, then while the next token is `+` or `-`, consumes the
     operator and another `term`, folding left-to-right (guarantees left-associativity).
   - `parse_term`: same shape but for `*` and `/`.
   - `parse_factor`: if the next token is `(`, recurse into `parse_expr` and consume the
     matching `)`; otherwise return the integer literal.

## Edge cases
- Multiple/leading/trailing spaces, and multi-digit numbers.
- Left-associativity for `-` and `/` (`10-2-3 == 5`, `8/4/2 == 1.0`), handled by iterative
  folding rather than recursion on the right.
- Nested and redundant parentheses.
- A bare number or a fully parenthesized expression.
- `/` producing float even for evenly divisible operands.

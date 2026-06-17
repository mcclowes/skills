# Plan: eval_expr

## Contract
- Input: a string `expr` containing a well-formed arithmetic expression. Tokens are non-negative integers, the binary operators `+ - * /`, parentheses `(` `)`, and arbitrary spaces.
- Output: a number. Integer when no division has produced a float and the value is integral by construction; float whenever `/` is involved (true division). I will let Python's arithmetic decide: integer `+ - *` on ints stay ints, and `/` always yields a float, matching the examples (`8 / 4 / 2 -> 1.0`, `2 + 3 * 4 -> 14`).

## Algorithm
I'll use a tokenizer plus a recursive-descent parser with a grammar that encodes precedence and left-associativity:

```
expr   := term (('+' | '-') term)*
term   := factor (('*' | '/') factor)*
factor := NUMBER | '(' expr ')'
```

1. Tokenize: scan characters, skip spaces, accumulate consecutive digits into integer tokens, emit single-char tokens for operators and parens.
2. Parse with an index/position cursor:
   - `parse_expr`: parse a `term`, then while the next token is `+`/`-`, consume it and fold the next `term` into the accumulator left-to-right (guarantees left-associativity, so `10 - 2 - 3 = 5`).
   - `parse_term`: same shape with `*`/`/`.
   - `parse_factor`: if `(`, recurse into `parse_expr` and consume `)`; else return the integer value.

## Edge cases
- Multi-digit numbers and leading/trailing/internal spaces (tokenizer handles).
- Deeply nested parentheses (recursion handles).
- Single-number expression (`parse_factor` returns directly).
- Multi-digit numbers like `100`.
Input is guaranteed well-formed, so no error handling for malformed input is required.

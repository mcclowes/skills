# Plan: eval_expr

## Contract
`eval_expr(expr: str) -> int | float`. Input is a well-formed arithmetic
expression containing non-negative integers, the binary operators `+ - * /`,
parentheses, and arbitrary spaces. Output is the evaluated numeric result:
multiplication and division produce floats only when division is involved
(`/` is true division and always yields a float), while `+ - *` over integers
stay integers. Standard precedence applies (`*`/`/` bind tighter than `+`/`-`),
operators are left-associative, and parentheses override precedence.

## Approach
I'll use a recursive-descent parser over a token stream, which cleanly encodes
precedence and associativity without manual operator-stack juggling.

1. **Tokenize.** Scan the string left to right. Skip spaces. Accumulate
   consecutive digits into one integer token. Emit single-character tokens for
   `+ - * / ( )`. Produce a list of tokens.
2. **Parse with three levels:**
   - `parse_expr`: parses a `term`, then while the next token is `+` or `-`,
     consumes it and another term, folding left-to-right (guarantees
     left-associativity, so `10 - 2 - 3 = 5`).
   - `parse_term`: same structure for `*` and `/`.
   - `parse_factor`: if the next token is `(`, recurse into `parse_expr` and
     consume the matching `)`; otherwise return the integer literal.
   I'll track a position index into the token list, advancing as I consume.

## Edge cases
- Leading/trailing/internal extra spaces: handled by skipping whitespace.
- Multi-digit numbers: accumulated during tokenization.
- Deeply nested parentheses: handled by recursion.
- Division yielding floats (`8/4/2 -> 1.0`): Python's `/` gives this naturally.
- A bare number with no operators: returns that integer.
- Left-associativity for both `- ` and `/`: enforced by the while-loop folding.

No unary minus or exponent need handling per the spec.

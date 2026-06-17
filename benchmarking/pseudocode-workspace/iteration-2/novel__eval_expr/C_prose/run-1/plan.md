# Plan: eval_expr

## Input/output contract
- Input: a string `expr` containing a well-formed arithmetic expression. Tokens are non-negative integers, the binary operators `+ - * /`, parentheses `( )`, and arbitrary spaces. No unary minus, no exponentiation, always well-formed.
- Output: a number. Integer literals are read as `int`; `/` always produces a `float` (true division); `+ - *` preserve types per Python semantics (so an all-integer expression with no division returns an `int`).

## Algorithm
A classic recursive-descent parser over a token stream, mirroring the grammar of standard precedence:

```
expr   := term  (('+' | '-') term)*
term   := factor (('*' | '/') factor)*
factor := NUMBER | '(' expr ')'
```

1. **Tokenize.** Scan the string left to right. Skip spaces. Accumulate consecutive digit characters into a single integer literal. Emit each operator/parenthesis as its own single-character token.
2. **Parse with a cursor.** Keep an index into the token list. `parse_expr` parses a `term`, then while the next token is `+`/`-`, consumes the operator, parses the next `term`, and folds left-associatively. `parse_term` does the same with `*`/`/` over `factor`. `parse_factor` returns a number literal, or consumes `(`, recurses into `parse_expr`, then consumes `)`.
3. Left-to-right folding inside each level guarantees left-associativity (`10 - 2 - 3 == 5`, `8/4/2 == 1.0`).

## Edge cases
- Multi-digit numbers and surrounding/embedded whitespace handled by the tokenizer.
- Nested and leading parentheses handled by recursion.
- Division yields float by using `/`; integer-only chains stay `int`.
- Input assumed well-formed, so no error recovery is required, though the cursor logic naturally consumes balanced parentheses.

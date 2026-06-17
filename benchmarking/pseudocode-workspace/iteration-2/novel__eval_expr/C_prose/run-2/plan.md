# Plan: eval_expr

## Input/output contract
Input: a string `expr` containing a well-formed arithmetic expression made of
non-negative integers, the binary operators `+ - * /`, parentheses, and spaces.
Output: a number — an `int` when no division occurred along a path (operands and
`+ - *` preserve `int`), or a `float` whenever `/` is involved (true division
always yields `float`). The input is guaranteed well-formed, so no error handling
for malformed input is required.

## Algorithm
I'll use a recursive-descent parser, which naturally encodes precedence and
left-associativity without manual operator-precedence bookkeeping.

1. **Tokenize**: scan the string, skipping spaces. Emit integer tokens (consume
   consecutive digits, convert with `int`) and single-character operator/paren
   tokens. This produces a flat token list.

2. **Parse** with three mutually recursive levels, using an index cursor:
   - `expression` -> handles `+` and `-`: parse a `term`, then while the next
     token is `+`/`-`, consume it and fold in another `term`. Left-to-right
     looping gives left-associativity (so `10 - 2 - 3` = 5).
   - `term` -> handles `*` and `/` the same way over `factor`s, binding tighter
     because it sits below `expression`.
   - `factor` -> either a parenthesised `expression` (consume `(`, recurse,
     consume `)`) or an integer literal.

## Edge cases
- Single number, no operators -> returns that int.
- Nested/parenthesised groups override precedence.
- Multi-digit numbers and arbitrary spacing.
- `/` always returns float; `8 / 4 / 2` -> 1.0. Mixing keeps int unless a `/`
  participates on that subpath.

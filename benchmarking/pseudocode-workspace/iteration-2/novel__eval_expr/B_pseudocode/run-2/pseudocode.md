# eval_expr — recursive-descent arithmetic evaluator

Verdict: parser/evaluator over a grammar with precedence + associativity — plan first.

## Data & invariants
- Tokenize `expr` into tokens: integer literals (ints), operators `+ - * /`, parens `( )`. Spaces skipped.
- Parser holds a position `pos` into the token list.
  - Invariant: each parse function consumes exactly the tokens of the construct it parses, leaving `pos` on the next unconsumed token.
- Grammar (encodes precedence + left-assoc):
  - expr   := term  (("+"|"-") term)*
  - term   := factor (("*"|"/") factor)*
  - factor := NUMBER | "(" expr ")"
- Left-associativity comes from folding the `*` loop left-to-right (accumulate into a running value), not recursion on the right.
- `/` is true division → always float; `+ - *` on ints stay int.

## Control flow
Tokenize:
  i ← 0
  while i < len(s):
    if s[i] is space: i++; continue
    if s[i] is digit: read maximal run of digits → int token
    else: single-char token for one of ( ) + - * /; i++

parse_expr:
  value ← parse_term
  while next token is "+" or "-":
    op ← consume; rhs ← parse_term
    value ← value + rhs  (or - rhs)
  return value

parse_term:
  value ← parse_factor
  while next token is "*" or "/":
    op ← consume; rhs ← parse_factor
    value ← value * rhs   if op == "*"
    value ← value / rhs   if op == "/"   (true division)
  return value

parse_factor:
  if next token is "(":
    consume "("; value ← parse_expr; consume ")"; return value
  else:
    return consume NUMBER (as int)

top: tokens ← tokenize; pos ← 0; return parse_expr

## Edge cases
- single number "5" → factor returns 5, no operator loop runs → 5 (int).
- "10 - 2 - 3": loop folds left → (10-2)-3 = 5. Correct (not 11).
- "8 / 4 / 2": ((8/4)/2) = (2.0/2) = 1.0 float. Correct.
- "2 + 3 * 4": term binds 3*4=12 first, then 2+12=14.
- nested parens "((2))" → factor recurses through expr, fine.
- multi-digit numbers handled by maximal digit run.
- Input assumed well-formed: no error handling required for malformed input.

## Interface contract
- Input: well-formed expression string.
- Output: int when only + - * used on ints; float when any / applied (Python's / semantics propagate naturally).
- Pure; no mutation of input.

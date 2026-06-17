# eval_expr — pseudocode plan

Verdict: parser/evaluator over a grammar with precedence + left-associativity — planning first.

## Data & invariants
- Tokens: list of items, each either an int value or one of `+ - * / ( )`.
- Recursive-descent over a token stream with a cursor `pos`.
  - Invariant: each parse_* function consumes exactly the tokens of its subexpression
    and leaves `pos` on the first token after it.
- Grammar (encodes precedence; recursion = precedence levels):
    expr   := term  (('+' | '-') term)*      # lowest precedence, left-assoc
    term   := factor (('*' | '/') factor)*    # higher precedence, left-assoc
    factor := number | '(' expr ')'
- Left-associativity invariant: operators fold left — acc starts at first operand,
  then `acc = acc OP next` in left-to-right token order. NOT recursion on the right.

## Control flow
Tokenize:
  scan chars; skip spaces; accumulate consecutive digits into one integer token;
  single-char tokens for + - * / ( ).

parse_expr:
  acc ← parse_term
  while next token is '+' or '-':
    op ← consume; rhs ← parse_term
    acc ← acc + rhs   or   acc - rhs
  return acc

parse_term:
  acc ← parse_factor
  while next token is '*' or '/':
    op ← consume; rhs ← parse_factor
    acc ← acc * rhs   or   acc / rhs   (true division → may yield float)
  return acc

parse_factor:
  if next is '(':  consume '('; v ← parse_expr; consume ')'; return v
  else: consume number token; return its int value

top: tokenize, pos←0, v←parse_expr, return v

## Edge cases & failure modes
- "10 - 2 - 3" → ((10-2)-3)=5, not 11 — guaranteed by left-fold loop, not right recursion.
- "8 / 4 / 2" → ((8/4)/2)=1.0 — true division always float; matches expected 1.0.
- "2 + 3 * 4" → term binds 3*4 first via deeper level → 14.
- multi-digit numbers (e.g. 10) → digit accumulation, not per-char.
- spaces anywhere → skipped in tokenizer.
- nested parens → handled by recursion into parse_expr from parse_factor.
- input always well-formed (per spec) → no error handling needed; no unary minus, no exponent.

## Interface contract
- Input: well-formed expression string.
- Output: int (from + - * and integer literals) or float (whenever / is applied).
- Pure; no mutation of input. No error path required.

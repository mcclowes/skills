# eval_expr — pseudocode plan

Verdict: parser/evaluator over a grammar with precedence and associativity — logic-heavy, plan first.

## Data & invariants
- Input: well-formed string of non-negative int literals, `+ - * /`, `(`, `)`, spaces.
- Tokenize into a list of tokens: numbers (int) and single-char operators/parens. Spaces dropped.
- Parser uses a cursor `pos` into the token list.
  - Invariant: each parse function consumes exactly the tokens of the sub-expression it recognises and leaves `pos` on the first unconsumed token.
- Grammar (recursive descent, encodes precedence + left-assoc):
  - `expr   := term (('+' | '-') term)*`      ← lowest precedence, left-assoc
  - `term   := factor (('*' | '/') factor)*`  ← higher precedence, left-assoc
  - `factor := NUMBER | '(' expr ')'`

## Control flow
Tokenize:
  - walk chars; if digit, accumulate consecutive digits into one int token; if op/paren, emit single token; if space, skip.

parse_expr:
  value ← parse_term
  while next token is '+' or '-':
    op ← consume
    rhs ← parse_term
    value ← value+rhs if '+' else value-rhs   # fold left → left-associative
  return value

parse_term:
  value ← parse_factor
  while next token is '*' or '/':
    op ← consume
    rhs ← parse_factor
    value ← value*rhs if '*' else value/rhs   # true division for '/'
  return value

parse_factor:
  if next token is '(':
    consume '('; v ← parse_expr; consume ')'; return v
  else:
    return consume NUMBER (as int)

Top: tokens ← tokenize(expr); result ← parse_expr; return result.

## Why left-assoc works
Folding into `value` inside the `while` loop, left to right, gives `((10-2)-3)=5`, not `10-(2-3)=11`. Same for `8/4/2 = ((8/4)/2) = 1.0`. A naive recursive `term op expr` would be right-associative — avoided.

## Edge cases & failure modes
- Single number `"42"` → factor returns 42, no loop bodies run → 42 (int).
- Multi-digit numbers → tokenizer accumulates digits (don't treat each digit separately).
- Nested parens `((2+3))` → parse_factor recurses through parse_expr.
- Division always float (Python `/`); other ops preserve int when both int.
  - So `2+3*4` → int 14; `8/4/2` → float 1.0. Matches spec types.
- Input guaranteed well-formed → no error handling for malformed input required.

## Interface contract
- Input: well-formed expression string.
- Output: int (if no division produced a float in the result path) or float (true division yields float).
- Pure; no mutation of input. No exceptions on valid input.

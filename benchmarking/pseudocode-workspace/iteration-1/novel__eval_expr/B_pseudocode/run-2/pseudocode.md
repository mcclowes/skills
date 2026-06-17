# eval_expr — pseudocode plan

Verdict: parser/evaluator over a grammar with precedence + parentheses. Logic-heavy, planning first.

## Data & invariants
- Tokens: list of items, each either an int literal or one of `+ - * / ( )`.
- Parser uses a position cursor `i` into the token list.
  - Invariant: every parse-* function consumes the tokens for exactly one grammar unit and leaves `i` pointing at the first unconsumed token.
- Recursive-descent grammar (encodes precedence + left-assoc):
  - expr   := term (('+' | '-') term)*        # lowest precedence
  - term   := factor (('*' | '/') factor)*    # higher precedence
  - factor := number | '(' expr ')'
- Left-associativity comes from the loop folding left: `acc = acc OP next`, not recursion on the right.

## Control flow
```
tokenize(expr):
  scan chars left→right
  skip spaces
  if digit: consume run of digits → int token
  if char in + - * / ( ): emit as operator/paren token
  return token list

parse(tokens):
  i = 0
  result = parse_expr()
  return result          # input well-formed ⇒ i ends at len(tokens)

parse_expr():            # + and -
  acc = parse_term()
  while current token is '+' or '-':
    op = consume
    rhs = parse_term()
    acc = acc + rhs   (or acc - rhs)     # left fold
  return acc

parse_term():            # * and /
  acc = parse_factor()
  while current token is '*' or '/':
    op = consume
    rhs = parse_factor()
    if op == '*': acc = acc * rhs
    else:         acc = acc / rhs        # TRUE division → float
  return acc

parse_factor():
  if current token is '(':
    consume '('
    val = parse_expr()
    consume ')'
    return val
  else:
    return int value of number token (consume it)
```

## Edge cases & failure modes
- Single number `"42"` → parse_factor returns 42, no loops run → 42 (int).
- Left-assoc subtraction `10 - 2 - 3` → ((10-2)-3)=5, not 11. Loop fold guarantees this.
- Left-assoc division `8 / 4 / 2` → ((8/4)/2)=1.0, float because `/`.
- Precedence `2 + 3 * 4` → term binds 3*4 first → 14.
- Parens `(2 + 3) * 4` → factor recurses into expr → 20.
- Multi-digit numbers → consume full digit run, not single chars.
- Spaces anywhere → skipped in tokenizer.
- Mixed int/float: `+ - *` keep int when both operands int (Python `int +int` → int); `/` always float. Matches spec (14 int, 1.0 float).
- Input always well-formed per spec → no error handling required.

## Interface contract
- Input: string `expr`. Output: int or float (Python numeric).
- Pure; no mutation of input. No unary minus / exponent (not in grammar).

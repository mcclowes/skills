# eval_expr — pseudocode plan

Verdict: parser/evaluator over a grammar with precedence + associativity. Logic-heavy, planning first.

## Data & invariants
- Tokenize input string into a token list: numbers (int), and single-char operators `+ - * / ( )`. Spaces dropped.
- Parse via recursive descent with a position cursor `pos` into the token list.
  - Invariant: each parse function consumes exactly the tokens of the sub-expression it matched, leaving `pos` at the first unconsumed token.
- Grammar (encodes precedence; recursion encodes left-associativity via loop, not right recursion):
  - expr   := term  (('+' | '-') term)*
  - term   := factor (('*' | '/') factor)*
  - factor := number | '(' expr ')'

## Control flow
tokenize(s):
  scan chars; build multi-digit integers; emit operators/parens; skip spaces.

parse(tokens):
  pos = 0
  value = parse_expr()
  return value

parse_expr():            # handles + and -, left-assoc
  acc = parse_term()
  while next token is '+' or '-':
    op = consume
    rhs = parse_term()
    acc = acc + rhs   if op == '+'  else  acc - rhs
  return acc

parse_term():            # handles * and /, left-assoc
  acc = parse_factor()
  while next token is '*' or '/':
    op = consume
    rhs = parse_factor()
    acc = acc * rhs   if op == '*'  else  acc / rhs   # true division → float
  return acc

parse_factor():
  if next token is '(':
    consume '('
    v = parse_expr()
    consume ')'
    return v
  else:
    return int(consume number token)

## Why loops not right-recursion
- `10 - 2 - 3`: loop accumulates `((10-2)-3)=5`, left-assoc. Right recursion would give `10-(2-3)=11` — wrong.
- `8 / 4 / 2`: `((8/4)/2)=1.0`. Same reasoning.

## Edge cases & failure modes
- Multi-digit numbers ("10") → tokenizer groups consecutive digits.
- Mixed `* /` precedence: `2 + 3 * 4` → term parses `3*4=12` before `+`. → 14.
- Parentheses override: `(2+3)*4` → 20.
- Division always yields float (true division); `2*4` stays int. Mixed expressions promote naturally.
- Input always well-formed (per spec): no unary minus, no exponent, no empty input, balanced parens. No error handling needed beyond trusting the grammar.

## Interface contract
- Input: well-formed expression string. Output: int (if no division produced a float) or float.
- Pure function; returns numeric value. Integer math stays int; `/` introduces float per Python true division.

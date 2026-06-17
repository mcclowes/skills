# eval_expr — pseudocode plan

Verdict: parser/evaluator over a grammar with precedence + left-associativity — planning first.

## Data & invariants
- Tokens: stream of numbers (int) and operator/paren chars `+ - * / ( )`.
- `pos`: index into token list; advances forward only. Invariant: each parse function consumes exactly the tokens of the subexpression it returns, leaving `pos` at the token after it.
- Grammar (recursive descent, precedence baked into levels):
  - expr   := term (('+' | '-') term)*      # lowest precedence, left-assoc
  - term   := factor (('*' | '/') factor)*  # higher precedence, left-assoc
  - factor := number | '(' expr ')'
- Left-associativity invariant: at each level, fold left-to-right — `acc = acc OP next`, never recurse right on same level.

## Control flow
1. Tokenize:
   - scan chars; skip spaces.
   - run of digits → int token.
   - single char `+ - * / ( )` → operator token.
2. parse_expr:
   - val ← parse_term
   - while next token is '+' or '-':
       op ← consume; rhs ← parse_term
       val ← val + rhs  (or val - rhs)
   - return val
3. parse_term:
   - val ← parse_factor
   - while next token is '*' or '/':
       op ← consume; rhs ← parse_factor
       val ← val * rhs  (or val / rhs)   # / is true division → float
   - return val
4. parse_factor:
   - if next is '(': consume '(', val ← parse_expr, consume ')'; return val
   - else: consume number token; return it
5. result ← parse_expr over full token list.

## Edge cases & failure modes
- `10 - 2 - 3` → left fold: (10-2)-3 = 5, not 11. Loop handles it.
- `8 / 4 / 2` → (8/4)/2 = 1.0; true division yields float throughout.
- single number `"42"` → parse_factor returns it, no operator loop runs.
- nested parens `((2))` → recursion bottoms out fine.
- multi-digit numbers and surrounding spaces → tokenizer groups digits, drops spaces.
- input always well-formed (per spec) → no error handling needed; no unary minus, no exponent.

## Interface contract
- Input: well-formed string.
- Output: int when no division produces a float and inputs are ints; float when `/` used (Python `/` always returns float). Mixed `+`/`*` of ints stays int.
- Pure; raises nothing for valid input.

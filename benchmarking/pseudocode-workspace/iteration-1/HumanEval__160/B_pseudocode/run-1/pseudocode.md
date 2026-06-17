# do_algebra — plan

Verdict: light planning. It's evaluation of an arithmetic expression with operator
precedence, so the risk is wrong precedence / association. Build a string expression
and let the language evaluate it with correct precedence rather than hand-rolling a
parser.

## Data & invariants
- `operator`: list of op tokens, each in {`+`, `-`, `*`, `//`, `**`}.
- `operand`: list of non-negative ints, length == len(operator) + 1, length >= 2.
- Invariant: interleave operand[0] op[0] operand[1] op[1] ... operand[n].
- Precedence must follow standard math: `**` > `*`,`//` > `+`,`-`; left-assoc except `**`.
  Relying on the language's own expression evaluation guarantees this.

## Control flow
```
expr ← string of operand[0]
for i from 0 to len(operator)-1:
    expr ← expr + operator[i] + str(operand[i+1])
return evaluate(expr) as integer arithmetic
```

## Edge cases
- minimal: one operator, two operands → "a op b".
- operands non-negative so no leading-unary-minus ambiguity.
- `//` and `**` are multi-char tokens — concatenated verbatim, no splitting issue.

## Contract
- Pure. Returns the numeric (int) result of the built expression.

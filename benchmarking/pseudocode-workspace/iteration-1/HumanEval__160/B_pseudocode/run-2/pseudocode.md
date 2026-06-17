# do_algebra — plan

Verdict: builds and evaluates an algebraic expression with **operator precedence** (`**` > `*`,`//` > `+`,`-`).
The risk is precedence and associativity, not wiring. Planning the tricky core.

## Data & invariants
- `operator`: list of op strings, each in {`+`, `-`, `*`, `//`, `**`}. length = n.
- `operand`: list of non-negative ints. length = n+1 (always ≥ 2).
- Invariant: expression interleaves operand[0] op[0] operand[1] op[1] ... operand[n].
- Standard math precedence must apply: `2 + 3 * 4 - 5 = 9`, not 15.
- `**` is right-associative; `*`,`//`,`+`,`-` are left-associative.

## Control flow
Rather than reimplement a precedence parser (off-by-one prone), build the canonical
Python expression string and evaluate it under Python's own precedence rules.

  expr ← string of operand[0]
  for i from 0 to n-1:
    expr ← expr + " " + operator[i] + " " + operand[i+1]
  return evaluate(expr) as an arithmetic expression

Python's expression grammar already encodes the exact precedence/associativity required
(`**` binds tighter than `*`//`, which bind tighter than `+`/`-`; `**` right-assoc).

## Edge cases & failure modes
- Minimum case: 1 operator, 2 operands → "a op b". Handled by loop running once.
- All operands non-negative, so no leading-unary-minus ambiguity in the built string.
- `//` floor division on non-negative ints → matches integer floor div; spec uses ints.
- `**` with 0 exponent / large exponent → Python handles; no special case needed.
- Tokens are trusted (spec guarantees valid ops), so no need to sanitise input.

## Interface contract
- Pure function. Inputs not mutated.
- Returns an int (Python arithmetic over ints yields int for these ops).
- Assumes well-formed input per spec (len(operator) == len(operand) - 1).

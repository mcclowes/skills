# Plan for `do_algebra`

## Input/output contract
The function takes two lists: `operator`, a list of strings drawn from the
basic algebra operators `+`, `-`, `*`, `//`, `**`; and `operand`, a list of
non-negative integers. The guaranteed invariant is `len(operator) ==
len(operand) - 1`, with at least one operator and at least two operands. The
function returns a single number (an `int` given integer operands and these
operators) equal to the evaluation of the algebraic expression formed by
interleaving operands and operators left to right.

## Algorithm
The cleanest, correct approach is to build the expression string and evaluate
it with Python's `eval`, because Python's own operator precedence and
associativity exactly match what the problem expects (e.g. `2 + 3 * 4 - 5`
yields `9`, `**` binds tighter than `*`, `//` is floor division). I interleave
each operand with the following operator: start with `str(operand[0])`, then for
each index `i` append ` operator[i] ` and ` str(operand[i+1])`. Wrapping tokens
in spaces avoids `**`/`//` being misread. I then `return eval(expression)`.

## Edge cases
- Minimal case: one operator, two operands — handled by the single loop pass.
- `**` right-associativity and precedence are handled natively by `eval`.
- `//` floor division semantics match Python directly.
- Non-negative operands mean no leading-minus parsing ambiguity arises;
  spacing further guards token boundaries.
- The stated invariants are assumed; no extra validation is added since the
  contract guarantees matching lengths and valid operators.

# Plan for do_algebra

## Input/output contract
- Inputs: `operator`, a list of strings drawn from `{+, -, *, //, **}`; `operand`, a list of non-negative integers.
- Guarantee: `len(operator) == len(operand) - 1`, `len(operator) >= 1`, `len(operand) >= 2`.
- Output: a single integer (or numeric value) equal to the evaluation of the algebraic expression built by interleaving operands and operators.

## Data involved
We interleave the two lists into one infix expression: operand[0], operator[0], operand[1], operator[1], ..., operand[n]. The expression must be evaluated respecting standard operator precedence and associativity, exactly as the docstring example shows: `2 + 3 * 4 - 5 = 9` (multiplication binds tighter than +/-), not left-to-right `(((2+3)*4)-5) = 15`.

## Algorithm steps
1. Build a string expression by walking through the operands, appending each operand, and inserting the corresponding operator between consecutive operands.
2. Concatenate with surrounding spaces so tokens like `//` and `**` are unambiguous.
3. Evaluate the resulting expression string using Python's `eval`, which already implements correct precedence (`**` > `*`//`//` > `+`/`-`) and left-to-right associativity for same-precedence operators (right-to-left for `**`). This precisely matches the intended algebra semantics.
4. Return the evaluated result.

## Edge cases
- Minimal case: one operator, two operands (handled by the loop naturally).
- Exponentiation with zero/large exponents: handled by `eval`.
- Floor division: operands are non-negative integers, division-by-zero is not part of the stated guarantees, so no special handling is required.
- Since operands are non-negative and inputs are trusted (built only from the given lists), `eval` is safe here.

The construction relies on the length invariant so every operator has a left and right operand.

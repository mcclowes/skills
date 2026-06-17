# Plan for do_algebra

## Input/output contract
- Inputs: `operator`, a list of operator strings drawn from `{'+', '-', '*', '//', '**'}`, and `operand`, a list of non-negative integers.
- Guarantee: `len(operator) == len(operand) - 1`, with at least one operator and at least two operands.
- Output: a single integer (or numeric value) — the result of evaluating the algebraic expression built by interleaving operands and operators.

## Data involved
The two lists are interleaved positionally: `operand[0] operator[0] operand[1] operator[1] operand[2] ...`. The example `['+', '*', '-']` with `[2, 3, 4, 5]` yields `2 + 3 * 4 - 5 = 9`, confirming that standard operator precedence applies — multiplication/exponentiation/floor-division bind tighter than addition/subtraction. This rules out a naive left-to-right fold; I must respect Python's precedence rules.

## Algorithm
The simplest correct approach is to build the expression as a string by interleaving the operands and operators, then evaluate it with Python's `eval`. Because the operator symbols (`+ - * // **`) are exactly Python's arithmetic operators, the built string is valid Python and `eval` honors the same precedence the spec intends. Steps:
1. Start the expression with `str(operand[0])`.
2. For each index `i` in `operator`, append the operator then `str(operand[i+1])`, separating tokens with spaces.
3. Return `eval(expression)`.

## Edge cases
- Single operator / two operands: handled naturally.
- Exponentiation (`**`) right-associativity and floor division (`//`) are handled correctly by `eval`.
- Operands are non-negative integers, so no unary-minus ambiguity. The input is trusted (operators are constrained), so `eval` is safe here.

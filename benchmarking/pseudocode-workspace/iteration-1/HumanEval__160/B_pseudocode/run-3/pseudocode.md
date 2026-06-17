# do_algebra — plan

Verdict: small logic core. The trap is operator precedence (** > * // > + -) and
left-to-right associativity. Hand-building eval would be the bug factory; instead
build the string and let a real precedence-aware evaluator handle it.

## Data & invariants
- operator: list of op tokens, each in {"+", "-", "*", "//", "**"}.
- operand: list of non-negative ints.
- Invariant: len(operator) == len(operand) - 1, len(operand) >= 2, len(operator) >= 1.
- Built expression interleaves operands and operators:
  operand[0] op[0] operand[1] op[1] ... op[n-1] operand[n].

## Control flow
- expr ← string(operand[0])
- for i in 0 .. len(operator)-1:
    expr ← expr + " " + operator[i] + " " + string(operand[i+1])
- result ← evaluate expr using standard arithmetic precedence + left assoc
- return result

## Edge cases & failure modes
- minimal: one operator, two operands → "a op b".
- precedence: "2 + 3 * 4 - 5" must = 9 (mult before add), not naive left-to-right.
- ** is right-associative, // truncates toward negative infinity (operands non-neg,
  so // behaves as floor of non-negatives — fine).
- no overlap/empty concerns: inputs guaranteed non-empty per spec.

## Interface contract
- Pure. Returns an int (or numeric result of the expression).
- Inputs not mutated.

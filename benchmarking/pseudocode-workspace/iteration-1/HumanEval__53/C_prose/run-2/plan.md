# Plan: add(x, y)

## Task
Implement a function `add` that takes two integers, `x` and `y`, and returns their sum. The provided docstring examples confirm the contract: `add(2, 3)` returns `5` and `add(5, 7)` returns `12`.

## Input/Output contract
- **Inputs**: `x: int` and `y: int`, two integer operands. Both are required positional parameters.
- **Output**: a single integer equal to the arithmetic sum `x + y`.
- The function is pure: it has no side effects, performs no I/O, and does not mutate its arguments (integers are immutable in Python regardless).

## Algorithm
The algorithm is a single arithmetic operation. Python's built-in `+` operator on two integers yields their exact sum, so the entire body reduces to `return x + y`. There is no iteration, recursion, branching, or auxiliary data structure required. No external imports are needed since integer addition is a core language feature.

## Edge cases
- **Negative numbers**: `+` handles negatives correctly (e.g. `add(-2, 5)` returns `3`), so no special handling is needed.
- **Zero**: adding zero returns the other operand unchanged.
- **Large magnitudes**: Python integers have arbitrary precision, so there is no overflow risk; very large values sum correctly.
- **Mixed sign / commutativity**: `x + y == y + x`, so argument order does not affect the result.

I will keep the original docstring with its doctest examples so the contract and examples remain documented and verifiable, and return the sum directly.

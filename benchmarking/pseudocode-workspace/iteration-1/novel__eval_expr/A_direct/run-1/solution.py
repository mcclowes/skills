def eval_expr(expr):
    """Evaluate a simple arithmetic expression and return an integer or float.

    Supported: non-negative integers, binary + - * /, parentheses, and spaces.
    Standard precedence: * and / bind tighter than + and -; left-associative;
    parentheses override. Division is true division (/ yields a float).

    No unary minus, no exponent. The input is always well-formed.

    Examples:
        eval_expr("2 + 3 * 4")      -> 14
        eval_expr("(2 + 3) * 4")    -> 20
        eval_expr("10 - 2 - 3")     -> 5      (left-assoc, not 11)
        eval_expr("8 / 4 / 2")      -> 1.0
    """
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            tokens.append(int(expr[i:j]))
            i = j
        else:
            tokens.append(c)
            i += 1

    pos = 0

    def parse_expression():
        nonlocal pos
        value = parse_term()
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            rhs = parse_term()
            value = value + rhs if op == '+' else value - rhs
        return value

    def parse_term():
        nonlocal pos
        value = parse_factor()
        while pos < len(tokens) and tokens[pos] in ('*', '/'):
            op = tokens[pos]
            pos += 1
            rhs = parse_factor()
            value = value * rhs if op == '*' else value / rhs
        return value

    def parse_factor():
        nonlocal pos
        token = tokens[pos]
        if token == '(':
            pos += 1
            value = parse_expression()
            pos += 1  # consume ')'
            return value
        pos += 1
        return token

    return parse_expression()

def eval_expr(expr):
    """Evaluate a simple arithmetic expression and return an integer or float."""
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c == ' ':
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
            if op == '+':
                value = value + rhs
            else:
                value = value - rhs
        return value

    def parse_term():
        nonlocal pos
        value = parse_factor()
        while pos < len(tokens) and tokens[pos] in ('*', '/'):
            op = tokens[pos]
            pos += 1
            rhs = parse_factor()
            if op == '*':
                value = value * rhs
            else:
                value = value / rhs
        return value

    def parse_factor():
        nonlocal pos
        tok = tokens[pos]
        if tok == '(':
            pos += 1  # consume '('
            value = parse_expression()
            pos += 1  # consume ')'
            return value
        pos += 1
        return tok

    return parse_expression()

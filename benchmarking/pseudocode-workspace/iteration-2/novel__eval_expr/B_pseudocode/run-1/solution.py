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

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def parse_expr():
        nonlocal pos
        acc = parse_term()
        while peek() in ('+', '-'):
            op = tokens[pos]
            pos += 1
            rhs = parse_term()
            acc = acc + rhs if op == '+' else acc - rhs
        return acc

    def parse_term():
        nonlocal pos
        acc = parse_factor()
        while peek() in ('*', '/'):
            op = tokens[pos]
            pos += 1
            rhs = parse_factor()
            acc = acc * rhs if op == '*' else acc / rhs
        return acc

    def parse_factor():
        nonlocal pos
        tok = peek()
        if tok == '(':
            pos += 1
            value = parse_expr()
            pos += 1  # consume ')'
            return value
        pos += 1
        return tok

    return parse_expr()

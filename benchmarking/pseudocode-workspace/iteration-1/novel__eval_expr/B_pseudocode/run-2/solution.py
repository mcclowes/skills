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

    def consume():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expr():
        acc = parse_term()
        while peek() in ('+', '-'):
            op = consume()
            rhs = parse_term()
            acc = acc + rhs if op == '+' else acc - rhs
        return acc

    def parse_term():
        acc = parse_factor()
        while peek() in ('*', '/'):
            op = consume()
            rhs = parse_factor()
            acc = acc * rhs if op == '*' else acc / rhs
        return acc

    def parse_factor():
        if peek() == '(':
            consume()
            val = parse_expr()
            consume()  # ')'
            return val
        return consume()

    return parse_expr()

def eval_expr(expr):
    """Evaluate a simple arithmetic expression and return an integer or float."""
    tokens = _tokenize(expr)
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expr():
        value = parse_term()
        while peek() in ('+', '-'):
            op = advance()
            rhs = parse_term()
            value = value + rhs if op == '+' else value - rhs
        return value

    def parse_term():
        value = parse_factor()
        while peek() in ('*', '/'):
            op = advance()
            rhs = parse_factor()
            value = value * rhs if op == '*' else value / rhs
        return value

    def parse_factor():
        tok = advance()
        if tok == '(':
            value = parse_expr()
            advance()  # consume ')'
            return value
        return tok

    return parse_expr()


def _tokenize(expr):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            tokens.append(int(expr[i:j]))
            i = j
        else:
            tokens.append(ch)
            i += 1
    return tokens

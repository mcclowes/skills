def eval_expr(expr):
    """Evaluate a simple arithmetic expression and return an integer or float."""

    def tokenize(s):
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c == ' ':
                i += 1
            elif c.isdigit():
                j = i
                while j < n and s[j].isdigit():
                    j += 1
                tokens.append(int(s[i:j]))
                i = j
            else:
                tokens.append(c)
                i += 1
        return tokens

    tokens = tokenize(expr)
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expression():
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
        tok = peek()
        if tok == '(':
            advance()
            value = parse_expression()
            advance()  # consume ')'
            return value
        return advance()

    return parse_expression()

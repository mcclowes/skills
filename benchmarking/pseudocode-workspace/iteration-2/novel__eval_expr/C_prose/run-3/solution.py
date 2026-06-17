def eval_expr(expr):
    """Evaluate a simple arithmetic expression and return an integer or float.

    Supported: non-negative integers, binary + - * /, parentheses, and spaces.
    Standard precedence: * and / bind tighter than + and -; left-associative;
    parentheses override. Division is true division (/ yields a float).
    """

    def tokenize(s):
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c.isspace():
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

    def consume():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_factor():
        tok = peek()
        if tok == '(':
            consume()
            value = parse_expr()
            consume()  # consume ')'
            return value
        return consume()

    def parse_term():
        value = parse_factor()
        while peek() in ('*', '/'):
            op = consume()
            rhs = parse_factor()
            if op == '*':
                value = value * rhs
            else:
                value = value / rhs
        return value

    def parse_expr():
        value = parse_term()
        while peek() in ('+', '-'):
            op = consume()
            rhs = parse_term()
            if op == '+':
                value = value + rhs
            else:
                value = value - rhs
        return value

    return parse_expr()

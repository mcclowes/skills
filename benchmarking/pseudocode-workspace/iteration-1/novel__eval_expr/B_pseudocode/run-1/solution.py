def eval_expr(expr):
    """Evaluate a simple arithmetic expression and return an integer or float.

    Supported: non-negative integers, binary + - * /, parentheses, and spaces.
    Standard precedence: * and / bind tighter than + and -; left-associative;
    parentheses override. Division is true division (/ yields a float).
    """
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c == " ":
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

    def parse_factor():
        nonlocal pos
        tok = tokens[pos]
        if tok == "(":
            pos += 1  # consume '('
            val = parse_expr()
            pos += 1  # consume ')'
            return val
        pos += 1  # consume number
        return tok

    def parse_term():
        nonlocal pos
        val = parse_factor()
        while peek() in ("*", "/"):
            op = tokens[pos]
            pos += 1
            rhs = parse_factor()
            if op == "*":
                val = val * rhs
            else:
                val = val / rhs
        return val

    def parse_expr():
        nonlocal pos
        val = parse_term()
        while peek() in ("+", "-"):
            op = tokens[pos]
            pos += 1
            rhs = parse_term()
            if op == "+":
                val = val + rhs
            else:
                val = val - rhs
        return val

    return parse_expr()

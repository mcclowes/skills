def do_algebra(operator, operand):
    expression = str(operand[0])
    for op, value in zip(operator, operand[1:]):
        expression += " " + op + " " + str(value)
    return eval(expression)

def do_algebra(operator, operand):
    expression = str(operand[0])
    for i, op in enumerate(operator):
        expression += " " + op + " " + str(operand[i + 1])
    return eval(expression)

def do_algebra(operator, operand):
    """
    Given two lists operator, and operand. The first list has basic algebra operations, and
    the second list is a list of integers. Use the two given lists to build the algebric
    expression and return the evaluation of this expression.
    """
    expression = str(operand[0])
    for op, value in zip(operator, operand[1:]):
        expression += op + str(value)
    return eval(expression)

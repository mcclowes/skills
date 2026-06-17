def count_nums(arr):
    def signed_digit_sum(n):
        digits = [int(d) for d in str(abs(n))]
        if n < 0:
            digits[0] = -digits[0]
        return sum(digits)

    return sum(1 for n in arr if signed_digit_sum(n) > 0)

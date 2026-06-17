def count_nums(arr):
    def signed_digit_sum(n):
        digits = [int(d) for d in str(abs(n))]
        total = sum(digits)
        if n < 0:
            total -= 2 * digits[0]
        return total

    return sum(1 for n in arr if signed_digit_sum(n) > 0)

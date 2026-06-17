def move_one_ball(arr):
    if not arr:
        return True

    n = len(arr)
    descents = sum(1 for i in range(n - 1) if arr[i] > arr[i + 1])

    if descents == 0:
        return True
    if descents == 1:
        return arr[-1] <= arr[0]
    return False

def move_one_ball(arr):
    n = len(arr)
    if n == 0:
        return True
    breaks = sum(1 for i in range(n) if arr[i] > arr[(i + 1) % n])
    return breaks <= 1

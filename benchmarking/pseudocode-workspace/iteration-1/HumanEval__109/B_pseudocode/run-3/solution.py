def move_one_ball(arr):
    if not arr:
        return True
    n = len(arr)
    drops = sum(1 for i in range(n) if arr[i] > arr[(i + 1) % n])
    return drops <= 1

def move_one_ball(arr):
    if not arr:
        return True
    n = len(arr)
    min_idx = arr.index(min(arr))
    rotated = arr[min_idx:] + arr[:min_idx]
    return all(rotated[i] <= rotated[i + 1] for i in range(n - 1))

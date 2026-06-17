import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = [int(x) for x in data[1:1 + n]]

    left = [0] * (n + 1)
    right = [0] * (n + 1)
    for v in a:
        right[v] += 1

    # S = sum over all v of left[v]*right[v]; starts at 0 since left all zero.
    s = 0
    ans = 0
    for v in a:
        # Move v out of the right side.
        old = left[v] * right[v]
        right[v] -= 1
        new = left[v] * right[v]
        s += new - old

        # v is the middle; exclude pairs of the same value.
        ans += s - left[v] * right[v]

        # Move v into the left side.
        old = left[v] * right[v]
        left[v] += 1
        new = left[v] * right[v]
        s += new - old

    print(ans)


main()

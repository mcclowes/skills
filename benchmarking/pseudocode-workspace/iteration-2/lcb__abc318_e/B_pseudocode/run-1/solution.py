import sys


def main() -> None:
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = [int(x) for x in data[1:1 + n]]

    # L[v] = count in prefix (strictly left of current j)
    # R[v] = count in suffix (current j and right, then adjusted)
    L = [0] * (n + 1)
    R = [0] * (n + 1)
    for v in a:
        R[v] += 1

    # S = sum over v of L[v] * R[v]; starts at 0 since L is all zero.
    S = 0
    answer = 0

    for v in a:
        # Step 1: remove v from R so neither side counts j itself.
        S -= L[v] * R[v]
        R[v] -= 1
        S += L[v] * R[v]

        # Step 2: valid middles = all matched pairs through j, minus those with A_i = A_j.
        answer += S - L[v] * R[v]

        # Step 3: move v into the prefix for the next middle.
        S -= L[v] * R[v]
        L[v] += 1
        S += L[v] * R[v]

    sys.stdout.write(str(answer) + "\n")


main()

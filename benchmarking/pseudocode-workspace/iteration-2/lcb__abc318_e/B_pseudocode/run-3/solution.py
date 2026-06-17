import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    a = data[1:1 + n]

    positions = {}
    for idx in range(n):
        v = a[idx]
        positions.setdefault(v, []).append(idx)

    answer = 0
    for P in positions.values():
        prefix = 0  # sum of P[0..b-1]
        for b in range(len(P)):
            # Term1 contribution for this b: P[b]*b - prefix
            term1 = P[b] * b - prefix
            # Term2 contribution: sum_{a<b}(b-a) = b*(b+1)//2
            term2 = b * (b + 1) // 2
            answer += term1 - term2
            prefix += P[b]

    sys.stdout.write(str(answer) + "\n")


main()

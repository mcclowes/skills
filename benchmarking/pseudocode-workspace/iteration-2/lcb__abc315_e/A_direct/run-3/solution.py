import sys
from sys import setrecursionlimit


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    prereq = [[] for _ in range(n + 1)]
    for i in range(1, n + 1):
        c = int(data[idx]); idx += 1
        lst = []
        for _ in range(c):
            lst.append(int(data[idx])); idx += 1
        prereq[i] = lst

    # We need all books reachable from book 1 (excluding book 1),
    # output in an order such that prerequisites come before dependents.
    # Iterative post-order DFS gives valid topological order.
    visited = [False] * (n + 1)
    order = []

    # iterative DFS post-order starting from 1
    stack = [(1, False)]
    visited[1] = True
    while stack:
        node, processed = stack.pop()
        if processed:
            if node != 1:
                order.append(node)
            continue
        stack.append((node, True))
        for nb in prereq[node]:
            if not visited[nb]:
                visited[nb] = True
                stack.append((nb, False))

    sys.stdout.write(" ".join(map(str, order)) + "\n")


if __name__ == "__main__":
    main()

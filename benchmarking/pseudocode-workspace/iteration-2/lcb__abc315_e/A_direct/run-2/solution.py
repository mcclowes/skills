import sys
from sys import setrecursionlimit


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    deps = [[] for _ in range(n + 1)]
    for i in range(1, n + 1):
        c = int(data[idx]); idx += 1
        lst = []
        for _ in range(c):
            lst.append(int(data[idx])); idx += 1
        deps[i] = lst

    # We only care about books reachable from book 1.
    # A book must be read after all its dependencies.
    # Iterative post-order DFS starting from book 1.
    order = []
    visited = [0] * (n + 1)  # 0 = unvisited, 1 = in progress, 2 = done

    stack = [(1, False)]
    while stack:
        node, processed = stack.pop()
        if processed:
            order.append(node)
            continue
        if visited[node] == 2:
            continue
        visited[node] = 2
        stack.append((node, True))
        for dep in deps[node]:
            if visited[dep] != 2:
                stack.append((dep, False))

    # order is post-order: dependencies come before dependents.
    # The last element is book 1; exclude it.
    result = [str(x) for x in order if x != 1]
    sys.stdout.write(" ".join(result) + "\n")


main()

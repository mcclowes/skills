import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1

    prereq = [None] * (n + 1)
    for i in range(1, n + 1):
        c = int(data[idx]); idx += 1
        if c:
            prereq[i] = [int(x) for x in data[idx:idx + c]]
            idx += c
        else:
            prereq[i] = []

    visited = [False] * (n + 1)
    result = []

    # Iterative post-order DFS from book 1 over prerequisite edges.
    # Stack frames are (node, is_exit).
    stack = [(1, False)]
    while stack:
        u, is_exit = stack.pop()
        if is_exit:
            if u != 1:
                result.append(u)
            continue
        if visited[u]:
            continue
        visited[u] = True
        stack.append((u, True))
        for p in prereq[u]:
            if not visited[p]:
                stack.append((p, False))

    sys.stdout.write(" ".join(map(str, result)))
    sys.stdout.write("\n")


main()

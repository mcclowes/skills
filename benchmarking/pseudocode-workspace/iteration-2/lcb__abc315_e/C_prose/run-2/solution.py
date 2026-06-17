import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1

    prereq = [[] for _ in range(n + 1)]
    for i in range(1, n + 1):
        c = int(data[idx]); idx += 1
        if c:
            prereq[i] = [int(x) for x in data[idx:idx + c]]
            idx += c

    visited = [False] * (n + 1)
    order = []

    # Iterative post-order DFS from book 1.
    # Stack entries: (node, is_exit)
    stack = [(1, False)]
    while stack:
        node, is_exit = stack.pop()
        if is_exit:
            order.append(node)
            continue
        if visited[node]:
            continue
        visited[node] = True
        stack.append((node, True))
        for p in prereq[node]:
            if not visited[p]:
                stack.append((p, False))

    # order ends with book 1 (post-order); drop it.
    result = [str(b) for b in order if b != 1]
    sys.stdout.write(" ".join(result) + "\n")


if __name__ == "__main__":
    main()

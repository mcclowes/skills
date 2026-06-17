import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    prereq = [[] for _ in range(n + 1)]
    for i in range(1, n + 1):
        c = int(data[idx]); idx += 1
        lst = prereq[i]
        for _ in range(c):
            lst.append(int(data[idx])); idx += 1

    visited = [False] * (n + 1)
    order = []

    # Iterative post-order DFS from book 1.
    stack = [(1, 0)]
    visited[1] = True
    while stack:
        node, ci = stack[-1]
        children = prereq[node]
        # advance to next unvisited child
        while ci < len(children) and visited[children[ci]]:
            ci += 1
        if ci < len(children):
            child = children[ci]
            stack[-1] = (node, ci + 1)
            visited[child] = True
            stack.append((child, 0))
        else:
            order.append(node)
            stack.pop()

    # order ends with book 1; exclude it.
    result = [str(b) for b in order if b != 1]
    sys.stdout.write(" ".join(result) + "\n")


if __name__ == "__main__":
    main()

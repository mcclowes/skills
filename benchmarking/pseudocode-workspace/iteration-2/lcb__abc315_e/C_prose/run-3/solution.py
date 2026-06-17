import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1

    prereq = [None] * (n + 1)
    for i in range(1, n + 1):
        c = int(data[idx]); idx += 1
        if c:
            prereq[i] = data[idx:idx + c]
            idx += c
        else:
            prereq[i] = []

    visited = [False] * (n + 1)
    order = []

    # Iterative post-order DFS from book 1 over prerequisite edges.
    stack = [(1, 0)]
    visited[1] = True
    while stack:
        node, ci = stack[-1]
        children = prereq[node]
        if ci < len(children):
            stack[-1] = (node, ci + 1)
            nxt = int(children[ci])
            if not visited[nxt]:
                visited[nxt] = True
                stack.append((nxt, 0))
        else:
            order.append(node)
            stack.pop()

    # order ends with book 1; exclude it.
    result = [str(x) for x in order if x != 1]
    sys.stdout.write(" ".join(result) + "\n")


if __name__ == "__main__":
    main()

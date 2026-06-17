import sys


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

    visited = [False] * (n + 1)
    order = []
    # Iterative DFS post-order from book 1.
    # stack entries: (node, child_index)
    stack = [(1, 0)]
    visited[1] = True
    while stack:
        node, ci = stack[-1]
        if ci < len(prereq[node]):
            stack[-1] = (node, ci + 1)
            nxt = prereq[node][ci]
            if not visited[nxt]:
                visited[nxt] = True
                stack.append((nxt, 0))
        else:
            order.append(node)
            stack.pop()

    # order is post-order; book 1 is last. Exclude it.
    result = [str(x) for x in order if x != 1]
    sys.stdout.write(" ".join(result) + "\n")


if __name__ == "__main__":
    main()

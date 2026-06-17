import sys
from collections import deque


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    prereq = [[] for _ in range(n + 1)]
    for i in range(1, n + 1):
        c = int(data[idx]); idx += 1
        for _ in range(c):
            p = int(data[idx]); idx += 1
            prereq[i].append(p)

    # Find all books needed (reachable from book 1's prerequisites)
    needed = [False] * (n + 1)
    stack = [1]
    needed[1] = True
    while stack:
        cur = stack.pop()
        for p in prereq[cur]:
            if not needed[p]:
                needed[p] = True
                stack.append(p)

    # Build graph among needed books: edge p -> i (p must be read before i)
    # Topological order via Kahn's algorithm on indegree.
    indeg = [0] * (n + 1)
    adj = [[] for _ in range(n + 1)]
    for i in range(1, n + 1):
        if not needed[i]:
            continue
        for p in prereq[i]:
            # p is prerequisite of i; p before i
            adj[p].append(i)
            indeg[i] += 1

    q = deque()
    for i in range(1, n + 1):
        if needed[i] and indeg[i] == 0:
            q.append(i)

    order = []
    while q:
        cur = q.popleft()
        order.append(cur)
        for nxt in adj[cur]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)

    # Exclude book 1 (it is last in topo order)
    result = [str(x) for x in order if x != 1]
    sys.stdout.write(" ".join(result) + "\n")


main()

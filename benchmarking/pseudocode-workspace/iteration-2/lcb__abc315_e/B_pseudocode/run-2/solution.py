import sys


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    prereq = [None] * (n + 1)
    for i in range(1, n + 1):
        c = int(data[idx]); idx += 1
        lst = data[idx:idx + c]
        idx += c
        prereq[i] = [int(x) for x in lst]

    # Iterative post-order DFS from book 1 over prerequisite edges.
    # A book is appended only after ALL its (reachable) prerequisites are done.
    # state: 0=unseen, 1=in progress (on stack), 2=done.
    # Each stack frame is (node, is_exit). On first pop we push the exit frame
    # then push unseen children; the exit frame appends the node to order, so a
    # node is emitted strictly after every prerequisite has been emitted.
    state = [0] * (n + 1)
    order = []
    stack = [(1, False)]
    while stack:
        u, is_exit = stack.pop()
        if is_exit:
            order.append(u)
            state[u] = 2
            continue
        if state[u] != 0:
            continue  # already visited via another path
        state[u] = 1
        stack.append((u, True))
        for p in prereq[u]:
            if state[p] == 0:
                stack.append((p, False))

    # order ends with book 1 (appended last); strip it.
    result = [str(x) for x in order if x != 1]
    sys.stdout.write(" ".join(result) + "\n")


main()

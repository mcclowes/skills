# Plan

## Problem
We have N books. Book i requires reading C_i prerequisite books (listed as P_{i,j}) before it can be read. We want the minimum set of books needed to read book 1, printed in a valid reading order (excluding book 1). The set is uniquely determined; any valid topological order is acceptable.

## Data
- Adjacency: for each book i, store its list of prerequisites `prereq[i]`.
- We only care about books transitively required by book 1.

## Algorithm
This is a dependency/topological ordering problem restricted to the subgraph reachable from book 1 via prerequisite edges.

1. Parse N and each line: C_i followed by C_i prerequisite ids.
2. Do a DFS (iterative to avoid recursion limits at N up to 2e5) starting from book 1. A post-order DFS over prerequisite edges naturally yields a valid reading order: a book is appended to the output only after all of its prerequisites have been appended. This guarantees every prerequisite precedes the book that needs it.
3. Mark nodes as visited so each is processed once. The total work is bounded by sum of C_i (<= 2e5), so linear.
4. The post-order traversal from book 1 produces book 1 last; we exclude book 1 from the output (everything else is the answer in order).

## Iterative post-order
Use an explicit stack of (node, child_index) frames. When a node's children are all explored, append it to the result and pop. Visited marking happens when a node is first pushed to avoid revisiting.

## Edge cases
- Book 1's prerequisites may themselves have prerequisites (deep chains) — handled by DFS.
- Books not required by book 1 are never visited.
- Large input: read all stdin at once, iterative DFS, fast output via join.
- A prerequisite appearing in multiple lists is read only once (visited set).

## I/O contract
- Input: N on line 1, then N lines each `C_i P_{i,1} ... P_{i,C_i}`.
- Output: space-separated book numbers (excluding book 1) in a valid reading order.

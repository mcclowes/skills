# Plan

## Problem restatement
Each book `i` has a list of prerequisite books `P[i]` that must be read before it. We must
read book 1, and want the minimum set of books (transitive prerequisites of book 1),
printed in a valid reading order excluding book 1. The set is uniquely determined; any
valid topological order works.

## Data
- `N`: number of books.
- `prereq[i]`: list of prerequisite book indices for book `i` (1-based).
- We only care about books reachable from book 1 by following prerequisite edges.

## Algorithm
This is a dependency/topological-ordering problem restricted to the books needed for
book 1.

1. Read input, storing `prereq[i]` for each book.
2. Find the set of books required: do a DFS/BFS from book 1 over the prerequisite edges
   (`i -> P[i,j]`). Only these books matter.
3. Produce a topological order such that every book appears after all its prerequisites.
   The natural way: an iterative post-order DFS starting at book 1. When a node finishes
   (all its prerequisites have been emitted), append it to the result. This guarantees
   each book comes after its prerequisites.
4. The post-order from book 1 ends with book 1 itself; drop book 1, output the rest in
   order. The remaining order is a valid reading order.

I use an explicit stack to avoid Python recursion-limit issues (N up to 2*10^5).
Each node is pushed; on first visit we push its unvisited prerequisites; on second visit
(children done) we append it to the order. A `visited` set prevents re-processing, and a
state marker (enter vs exit) drives the post-order emission.

## Edge cases
- Book 1 has prerequisites guaranteed (`C_1 >= 1`), so output is non-empty.
- Shared prerequisites (a book required by several) are emitted once, handled by `visited`.
- Deep chains: iterative stack avoids recursion overflow.
- Books not reachable from 1 are never visited, so excluded automatically.

## I/O contract
- Input: first line `N`; next `N` lines each `C_i` followed by `C_i` book numbers.
- Output: space-separated book numbers (excluding book 1) in valid reading order.

# Plan: minimum books to read book 1

Verdict: topological/dependency traversal with a subtle "only books reachable from 1"
restriction and ordering invariant — planning first.

## Data & invariants
- `prereq[i]` = list of books that must be read before book i (the C_i prerequisites).
- The required set = all books reachable from book 1 by following prereq edges (the
  transitive closure of dependencies), excluding book 1 itself.
- Invariant: a book may be printed only after ALL of its prerequisites (that are in the
  required set) have already been printed. This is a topological order of the dependency
  DAG restricted to the reachable set.
- Graph is a DAG (problem guarantees readability ⇒ no cycles among required books).

## Control flow
1. Read N and prereq lists.
2. Find reachable set R: BFS/DFS from book 1 over prereq edges. Mark visited.
   (Only these books matter; unreachable books are ignored entirely.)
3. Topological sort restricted to R, using post-order DFS:
   - DFS(u): for each prerequisite p of u (p in R), if not yet emitted, recurse;
     after all prerequisites handled, append u to order.
   - Start DFS from book 1. Because we append AFTER recursing into prereqs,
     prerequisites land before dependents.
   - Use iterative DFS to avoid recursion-depth limit (N up to 2e5).
4. The produced post-order, with book 1 removed (it is appended last), is a valid order.

## Edge cases & failure modes
- Book with C_i = 0 in R: emitted immediately (no prereqs), fine.
- Diamond dependency (book reached via two paths): "emitted" flag prevents double output.
- Book 1 itself: appears last in post-order; strip it before printing.
- Books not reachable from 1: never visited, never printed — correct.
- Deep chains (sample 2): iterative stack handles depth 2e5 without overflow.

## Interface contract
- Input: stdin in the given format.
- Output: space-separated book numbers (excluding book 1) in a valid read order,
  followed by newline. Empty line if somehow nothing needed (cannot happen since C_1≥1).

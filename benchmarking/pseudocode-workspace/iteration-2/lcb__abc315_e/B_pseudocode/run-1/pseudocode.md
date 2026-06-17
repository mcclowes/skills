# Plan: minimum books to read book 1 (topological order)

Verdict: logic-heavy — DFS/topo sort with reachability restriction and ordering
invariant. Plan first.

## Data & invariants
- prereq[i] = list of books that must be read before book i (the P_{i,j}).
- We only care about books reachable from book 1 via prereq edges (transitive
  closure). Other books are irrelevant.
- Output = a valid order to read all books reachable from 1, EXCLUDING book 1
  itself, such that every book appears after all its prerequisites.
- Invariant: when a book is appended to the order, all of its prerequisites are
  already in the order.
- The SET of required books is unique (all books reachable from 1); only the
  order may vary. Any valid topo order is accepted.

## Control flow (post-order DFS from book 1)
- A standard post-order DFS over prereq edges yields a topological order:
  a node is emitted only after all nodes it depends on.
  order ← empty list
  visited ← all false
  DFS(node):
    mark node visited
    for each p in prereq[node]:
      if not visited[p]: DFS(p)
    append node to order
  call DFS(1)
- After DFS, `order` lists prerequisites before dependents, ending with book 1.
- Answer = order with book 1 removed (it is the last element, since it is the
  root and appended last).

## Iterative DFS (avoid recursion limit; N up to 2e5)
- Use explicit stack of (node, index_into_prereq_list).
- visited marked when first pushed (so we never push the same node twice).
- On entering a frame, iterate its prereq children; push unvisited child, pause
  current frame (save index). When all children done, append node to order.
- Concretely, stack holds frames; each step either descends into next unvisited
  child or, if none remain, pops and appends node.

## Edge cases
- Book with C_i = 0 (no prereqs): DFS appends it immediately. Fine.
- Books not reachable from 1: never visited, never output. Correct.
- A prerequisite shared by multiple books: visited guard ensures it is emitted
  once, before all its dependents (DFS guarantees ordering for each path). Fine.
- Cycle: problem guarantees readable (a DAG over reachable set), so no cycle.
- book 1 must be excluded from output: it is the last appended; drop it.

## Contract
- Read N, then N lines each "C_i P...".
- Print the required books (excluding 1) space-separated on one line.

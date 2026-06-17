# Plan: minimal prerequisite reading order for book 1

Verdict: logic-heavy (graph reachability + topological order on dependency
DAG). Planning first.

## Data & invariants
- prereq[i] = list of books that must be read before book i (the P_{i,j}).
- We only care about books *required* to read book 1: the set R of all books
  reachable from book 1 by following prereq edges, EXCLUDING book 1 itself.
  Invariant: this set is uniquely determined (problem guarantees it).
- A valid output is any topological order of R where every prerequisite of a
  book appears before it. Edge direction for topo: prereq -> dependent.

## Control flow
1. Read N, then for each book i (1..N) read C_i and its prereq list.
2. Compute R = set of books required for book 1:
   - BFS/DFS from book 1 over prereq edges.
   - Mark book 1 as "in closure" but it is NOT part of output.
   - For each book popped, push its prereqs if not yet seen.
   Invariant: every book in R is genuinely needed; books not reachable from 1
   are ignored entirely (sample 3: only book 5 reachable -> output "5").
3. Topological order of R only (do not include book 1, do not include
   irrelevant books). Use Kahn's algorithm restricted to R:
   - Build graph among R: for book u in R, for each prereq p of u (p also in R,
     which it always is since R is closed under prereqs), add edge p -> u and
     indegree[u] += 1.
   - Queue all R-books with indegree 0.
   - Pop, append to result, decrement indegree of dependents, enqueue when 0.
   Result is the order; book 1's own prereqs naturally end up before book 1
   conceptually but book 1 is excluded.

   Simpler equivalent: post-order DFS from book 1 over prereqs, appending a
   book after all its prereqs are appended; skip appending book 1. This yields
   a valid topo order directly. I'll use iterative DFS post-order to avoid
   recursion-depth limits (N up to 2e5).

## Iterative post-order DFS (chosen)
- visited[] boolean over books.
- stack of (node, child_index) frames OR two-state (enter/exit) markers.
- Use explicit stack with state flag:
  - push (1, ENTER).
  - while stack:
    - (u, st) = pop
    - if st == ENTER:
        if visited[u]: continue
        visited[u] = true
        push (u, EXIT)
        for each prereq p of u: if not visited[p]: push (p, ENTER)
    - else (EXIT):
        if u != 1: append u to result
  Note: marking visited on ENTER prevents duplicate processing; checking
  visited at ENTER-pop handles the case a node was queued twice before
  visiting. Post-order via EXIT marker guarantees all prereqs of u are output
  before u.
- Because we mark visited at first ENTER and re-check, each node processed once;
  EXIT always fires once per visited node -> correct post-order.

Edge subtlety: a prereq could be pushed ENTER multiple times by different
parents before being visited. The `if visited[u]: continue` at ENTER-pop guards
this; visited set at first real enter, EXIT scheduled exactly once at that time.

## Edge cases
- C_1 >= 1 guaranteed, so output is non-empty.
- Books with C_i = 0 and not reachable from 1: never visited, not output.
- Diamond dependencies (book reachable via two paths, sample 1: book 5 via
  book 2 and book 4): visited guard ensures it appears once, post-order ensures
  it appears before both dependents.
- Large N/sum C_i (2e5): iterative DFS, O(N + sum C). No recursion.
- Self/cycle: problem guarantees readable (DAG), so no cycle handling needed.

## Interface contract
- Input: stdin in given format.
- Output: space-separated book numbers (excluding book 1) in a valid read order,
  single line. Any valid order accepted.

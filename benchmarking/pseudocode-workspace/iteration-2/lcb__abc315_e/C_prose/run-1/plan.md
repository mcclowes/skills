# Plan

## Problem restatement
Each book `i` has a list of prerequisite books `P[i]` that must be read before it.
We want the minimal set of books needed to read book 1, then output a valid reading
order of that set (excluding book 1 itself).

## Data
- `N` books.
- `prereq[i]`: list of prerequisites for book `i` (1-indexed).

## Algorithm
The set of books required to read book 1 is exactly all books reachable from book 1
via the prerequisite edges (the transitive closure of dependencies). This set is
uniquely determined.

A valid reading order is any topological order restricted to that reachable set, where
a book appears after all of its prerequisites. Equivalently, a DFS post-order from
book 1 (visiting prerequisites recursively, then recording the current book) yields an
order in which every book comes after its prerequisites. Reversing isn't needed if we
append a book after recursing into its prerequisites: when we finish all prerequisites
of `x`, `x` itself goes onto the output list. So post-order gives prerequisites first.

Steps:
1. Read input, build `prereq`.
2. Iterative DFS from book 1 (recursion limit risk with N up to 2e5, so use an
   explicit stack). Mark visited. Produce post-order over reachable nodes.
3. The post-order naturally lists each node after its prerequisites. Remove book 1
   (it will be the last element of the post-order). Output the rest space-separated.

## Edge cases
- Large N (2e5): use iterative DFS to avoid stack overflow; fast IO via sys.stdin.
- A prerequisite may be shared by multiple books: visited set prevents duplicates and
  ensures each appears once.
- Only books reachable from 1 are included; unrelated books are ignored.

## I/O contract
Input: `N`, then N lines each `C_i` followed by `C_i` prerequisite book numbers.
Output: space-separated book numbers (excluding book 1) in a valid reading order.

# Plan: Minimum travel time (car then train)

## Data
- N cities, integer weights A, B, C.
- D is an N x N symmetric distance matrix, D[i][i] = 0.

## Model
We travel from city 1 to city N. Initially we use the company car; at some
city we may switch (once, irreversibly) to the train. Car edge cost between
cities i, j is D[i][j] * A; train edge cost is D[i][j] * B + C.

The cleanest formulation is a graph with two layers:
- Layer 0 = "still driving the car" state.
- Layer 1 = "now on the train" state.

Edges:
- Within layer 0: (i,0) -> (j,0) with cost D[i][j] * A (drive).
- Within layer 1: (i,1) -> (j,1) with cost D[i][j] * B + C (ride train).
- Switch (free, only in a city): (i,0) -> (i,1) with cost 0.

We never go from layer 1 back to layer 0, matching "cannot switch back".
Start node = (1, 0). The answer is min(dist(N,0), dist(N,1)), i.e. we may
arrive still driving, or having switched.

## Algorithm
Run Dijkstra over the 2N nodes. The graph is dense (every pair connected),
so a simple O(N^2) Dijkstra (no heap, linear scan for the min) is ideal and
fast enough for N <= 1000 (2000 nodes, ~4M relaxations).

## Edge cases
- Direct car-only or train-only trips are naturally covered.
- C is paid per train segment; the layered model pays C exactly when each
  train edge is taken, which is correct.
- Costs can be large (D, A, B up to 1e6, N up to 1000): use Python ints
  (arbitrary precision), no overflow concern. Use a large INF.
- D[i][i] = 0 edges are harmless.

## I/O contract
- Read N, A, B, C, then N rows of N integers.
- Print a single integer: the minimum total time.

# Plan

## Problem

Travel from city 1 to city N. Edge i-j has distance D[i][j]. By car, an edge
costs D*A; by train it costs D*B+C. You may switch from car to train (never
back), and only at a city, at no time cost. Minimise total travel time.

## Modelling

Build a graph with two layers of N nodes:

- Layer 0 (car layer): node i represents being in city i while still allowed to
  use the car.
- Layer 1 (train layer): node i represents being in city i having committed to
  train only.

Edges:

- Within layer 0: between every pair i,j a car edge of weight D[i][j]*A.
- Within layer 1: between every pair i,j a train edge of weight D[i][j]*B+C.
- From layer 0 node i to layer 1 node i: weight 0 (switch to train, free, in a
  city). The switch is monotone (only 0 -> 1), enforcing "no switch back".

Start at layer-0 node 1. The answer is the minimum of the shortest-path distance
to layer-0 node N and layer-1 node N (we might finish still on car, or on train).
Since the 0->1 transition is free and present at every city, we can equivalently
just answer dist to layer-1 node N after adding a free 0->1 at node N — but
taking the min over both layers is clearest and correct.

## Algorithm

Dijkstra over 2N nodes. The graph is dense (complete within each layer), so an
O(V^2) Dijkstra without a heap is appropriate for N up to 1000 (2N = 2000 nodes,
V^2 = 4,000,000 relaxations per extraction-ish; total O((2N)^2) ~ 16M, fine).

I'll implement an O(V^2) array-based Dijkstra.

## Edge cases

- D[i][i] = 0; staying put costs nothing useful but harmless.
- Large numbers: distances up to 10^6, A,B,C up to 10^6, N up to 1000, so paths
  can reach ~10^12 — Python big ints handle this. Use a large INF.
- Always reachable (complete graph), so the answer is finite.

## I/O contract

Input: first line N A B C; then N lines each with N integers (the D matrix).
Output: single integer, the minimum time.

# Plan

## Problem
Travel from city 1 to city N. Two transport modes between cities i and j: company
car costs `D[i][j] * A`, train costs `D[i][j] * B + C`. You may switch from car to
train (irreversibly) at any city for free. Minimise total travel time.

## Model
Once you switch to train you can never go back, so the journey is split into two
phases: a car-only prefix (city 1 ... some pivot city k), then a train-only suffix
(city k ... city N). The switch happens at some city k (possibly k=1, meaning train
the whole way, or k=N, meaning car the whole way). The graph is complete.

## Algorithm
1. Run Dijkstra from city 1 using only the car edge weights `D[i][j] * A`. This gives
   `carDist[k]` = minimum time to reach every city k by car only.
2. Run Dijkstra from city N (reversed; graph is symmetric so it's the same) using only
   the train edge weights `D[i][j] * B + C`. This gives `trainDist[k]` = minimum time
   to reach city N from city k by train only.
3. Answer = min over all pivot cities k of `carDist[k] + trainDist[k]`.

Because edges are symmetric, Dijkstra from N over train edges gives shortest train
distance from any node to N. Using two separate shortest-path computations and joining
at the pivot correctly captures the single car-to-train transition.

## Complexity
N up to 1000, complete graph with N^2 edges. A simple O(N^2) Dijkstra (no heap) per
run is fine: total O(N^2).

## Edge cases
- k=1: pure train path. k=N: pure car path. Both covered by the min over all k.
- Large values: car distance up to 1000*1e6*1e6 = 1e15, plus train; use Python ints
  (unbounded), no overflow concern.
- D[i][i]=0, self loops harmless.

## I/O contract
Input: first line `N A B C`; then N lines each with N integers (matrix D).
Output: single integer, the minimum travel time.
